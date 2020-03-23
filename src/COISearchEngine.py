# -*- coding: utf-8 -*-

# Import standart libs
import os
import argparse
from glob import glob
from collections import defaultdict
import shutil
import ntpath
import pandas as pd

# Import pdfminer
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBox, LTTextLine

# Import whoosh
from whoosh.fields import Schema, TEXT, ID
from whoosh import index
from whoosh.qparser import QueryParser
from whoosh.query import FuzzyTerm

# Import PyPDF2
from PyPDF2 import PdfFileWriter, PdfFileReader, PdfFileMerger
from PyPDF2.generic import DictionaryObject, NumberObject, FloatObject, NameObject, TextStringObject, ArrayObject

# Import YAML
from YAML import YAML

# Create Doc class
class Doc:
    """
    Doc - Class for pdf document
    """

    def __init__(self, name='', filepathPDF=''):
        """ Init Doc
            
        :param name:  Name of the pdf file
        :type name: str
        :param filepathPDF:Filepath of the pdf file
        :type filepathPDF: str
        """
        self.name = name                        #: Name of the pdf file
        self.filepathPDF = filepathPDF          #: Filepath of pdf file
        self.subdocs = []                       #: List of pdf documents used to create current document
        self.numpages = 0                       #: Number of pages
         
            
class DocSearch:
    """
    DocSearch - Class to search tags in pdf documents
    """
    def __init__(self, settingsfilepath='settings.yml'):
        """ Init DocSearch
            
        :param settingsfilepath: Filepath to settings.yml file
        :type settingsfilepath: str
        """
        
        self.docs = []                              #: List od documents (Doc class)
        self.doc_merge = Doc()                      #: Merged document
        self.results = []                           #: List of found results (list of dicts)
        self.ltObjList=[]                           #: List of found objects
        self.settingsfilepath = settingsfilepath    #: Settingsfilepath settingsfilepath.yml
        self.yaml = YAML()                          #: yaml handler
        
        # Create settings
        self.props = defaultdict(lambda: None,
            maxdist = 2,
            prefixlength = 1,
            folderpath_pdf='H:/cloud/cloud_data/Projects/COISE/documents',
            folderpath_result='H:/cloud/cloud_data/Projects/COISE/results',
            filename_merge='merge.pdf',
            filename_mark='mask.pdf',
            filename_result='result.xlsx',
            tags=['Introduction', 'Experiment'])
        
        # Load settings (yml file)
        if os.path.isfile(settingsfilepath):
            self.props = self.yaml.load(settingsfilepath)
        else:
            self.yaml.save(self.props, self.settingsfilepath)
        
    def __readDocs(self, folderpathPDF):
        files = glob(folderpathPDF + '/*.pdf')
        for f in files:
            doc = Doc(filepathPDF=f)
            with open(f, mode='rb') as file:
                reader = PdfFileReader(file)
                numpages = reader.getNumPages()
            doc.numpages = numpages
            head, file_extension = os.path.splitext(f)
            folderpath, filename = ntpath.split(head)
            doc.name = filename
            self.docs.append(doc)
        
    def merge(self, folderpathPDF='', filename_merge=''):
        """ Merge pdf documents to one merged document
            
        :param folderpathPDF: Path to folder containing all pdfs to merge
        :type folderpathPDF: str
        :param filename_merge: Name of the merged pdf file
        :type filename_merge: str
        """   
        
        # Update filepaths
        if not folderpathPDF:
            folderpath_pdf = self.props['folderpath_pdf']
        if not filename_merge:
            filename_merge = self.props['filename_merge']
        filepath_merge = os.path.join(self.props['folderpath_result'], filename_merge)
        
        # Create merge doc
        self.doc_merge = Doc(filepathPDF=filepath_merge)
        
        # Read docs
        self.__readDocs(folderpath_pdf)
        
        # Merge documents
        #pdf_merger = PdfFileMerger()
        pdf_merger = PdfFileMerger(strict=False)
        for d in self.docs:
            print('Merge document:', d.name)
            self.doc_merge.subdocs.append(d)
            if os.path.exists(d.filepathPDF):
                pdf_merger.append(d.filepathPDF)
            else:
                raise ValueError('Document ' + d.filepathPDF + ' does not exts.')
                
        # Write merged file to filepath_merged
        print('Write merge document to:', filepath_merge)
        with open(filepath_merge, 'wb') as file:
            pdf_merger.write(file)

    def getDocName(self, page):
        """ Extract document name py page number in merged pdf file
            
        :param page: Page number inmerged pdf document
        :type page: int
        """   
        
        numpages = 0
        for d in self.doc_merge.subdocs:
            numpages = numpages + d.numpages
            if numpages > page:
                return d.name
        
    def extractPDFText(self, filename_merge=''):
        """ Extract text form merged pdf file
            
        :param filename_merge: Filename of merged pdf file
        :type filename_merge: str
        """        
        
        # Update filepath
        if not filename_merge:
            filename_merge = self.props['filename_merge']
        filepath_merge = os.path.join(self.props['folderpath_result'], filename_merge)
        
        # Read number of pages
        with open(filepath_merge, mode='rb') as file:
            reader = PdfFileReader(file)
            numpages = reader.getNumPages()
            
        fp = open(filepath_merge, 'rb')
        parser = PDFParser(fp)
        doc = PDFDocument(parser)
        rsrcmgr = PDFResourceManager()
        laparams = LAParams()
        device = PDFPageAggregator(rsrcmgr, laparams=laparams)
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        for i, page in enumerate(PDFPage.create_pages(doc)):
            print('Extract text from page: ' + str(i) + ' / ' + str(numpages))
            interpreter.process_page(page)
            layout = device.get_result()
            #parse_layout(layout)
            for lt_obj in layout:
                if isinstance(lt_obj, LTTextBox) or isinstance(lt_obj, LTTextLine):
                    docname = self.getDocName(i)
                    self.ltObjList.append(dict({'OBJ': lt_obj, 'DOCNAME': docname, 'PAGE': i}))
        fp.close()

    def searchTags(self, tags=[]):
        """ Search tags in merged pdf file
            
        :param tags: List of search tags e.g. ['Introduction', 'Experiment']
        :type tags: list
        """         
        # Update tags
        if not tags :
            tags = self.props['tags']
        
        # Create custom FuzzyTerm for fuzzy tag search
        class CustomFuzzyTerm(FuzzyTerm):
            def __init__(self, fieldname, text, boost=1.0, maxdist=self.props['maxdist'], prefixlength=self.props['prefixlength'], constantscore=True):
                super(CustomFuzzyTerm, self).__init__(fieldname, text, boost, maxdist, prefixlength, constantscore)
        
        # Create teporary directory tmpdir
        if not os.path.exists("tmpdir"):
            os.mkdir("tmpdir")
            
        schema = Schema(title=TEXT(stored=True), path=ID(stored=True), content=TEXT(stored = True))
        ix = index.create_in("tmpdir", schema)
        writer = ix.writer()
        for i, ltObj in enumerate(self.ltObjList):
            writer.add_document(title=str(i), content=ltObj['OBJ'].get_text(), path=u"/a")
        writer.commit()
        
        results=[]
        id=0
        for tag in tags:
            print('Searching tag: ', tag)
            with ix.searcher() as searcher:
                 #query = QueryParser("content", ix.schema).parse(tag)
                 
                 qp = QueryParser("content", schema=ix.schema, termclass=CustomFuzzyTerm)
                 query = qp.parse(tag+'~4/4')
                 
                 res = searcher.search(query, limit=None)
                 for hit in res:
                     results.append(dict({
                         'ID': id, 
                         'DOCNAME': self.ltObjList[hit.docnum]['DOCNAME'],
                         'TAG': tag, 
                         'PAGE': self.ltObjList[hit.docnum]['PAGE'],
                         'HITNUM': hit.docnum,
                         'BBOX': self.ltObjList[hit.docnum]['OBJ'].bbox,
                         'TEXT': self.ltObjList[hit.docnum]['OBJ'].get_text()}))
                     id += 1
        self.results = results
        

            
        return results
    
    def create_highlight(self, x1, y1, x2, y2, meta, color=[0, 1, 0]):
        """
        Create a highlight for a PDF.
    
        Parameters
        ----------
        x1, y1 : float
            bottom left corner
        x2, y2 : float
            top right corner
        meta : dict
            keys are "author" and "contents"
        color : iterable
            Three elements, (r,g,b)
        """
        new_highlight = DictionaryObject()
    
        new_highlight.update({
            NameObject("/F"): NumberObject(4),
            NameObject("/Type"): NameObject("/Annot"),
            NameObject("/Subtype"): NameObject("/Highlight"),
    
            NameObject("/T"): TextStringObject(meta["author"]),
            NameObject("/Contents"): TextStringObject(meta["contents"]),
    
            NameObject("/C"): ArrayObject([FloatObject(c) for c in color]),
            NameObject("/Rect"): ArrayObject([
                FloatObject(x1),
                FloatObject(y1),
                FloatObject(x2),
                FloatObject(y2)
            ]),
            NameObject("/QuadPoints"): ArrayObject([
                FloatObject(x1),
                FloatObject(y2),
                FloatObject(x2),
                FloatObject(y2),
                FloatObject(x1),
                FloatObject(y1),
                FloatObject(x2),
                FloatObject(y1)
            ]),
        })
    
        return new_highlight
        
    def add_highlight_to_page(self, highlight, page, output):
        """
        Add a highlight to a PDF page.
    
        Parameters
        ----------
        highlight : Highlight object
        page : PDF page object
        output : PdfFileWriter object
        """
        highlight_ref = output._addObject(highlight)
    
        if "/Annots" in page:
            page[NameObject("/Annots")].append(highlight_ref)
        else:
            page[NameObject("/Annots")] = ArrayObject([highlight_ref])


    def markResults(self, filename_merge='', filename_mark=''):
        """ Highlight results in pdf file by a comment
            
        :param filename_merge: Name of the merged pdf file
        :type filename_merge: str
        :param filename_mark: Name of the highlighted pdf file
        :type filename_mark: str
        """    

        print('Highlight results in pdf file.')
        
        # Update filepath
        if not filename_merge:
            filename_merge = self.props['filename_merge']
        if not filename_mark:
            filename_mark = self.props['filename_mark']
        filepath_merge = os.path.join(self.props['folderpath_result'], filename_merge)
        filepath_mark = os.path.join(self.props['folderpath_result'], filename_mark)
        
        file_input = open(filepath_merge, "rb")
        pdf_input = PdfFileReader(file_input)
        numpages = pdf_input.getNumPages()
        pdf_output = PdfFileWriter()
        for p in range(0,numpages):
            page = pdf_input.getPage(p)
            for res in self.results:
                if res['PAGE'] == p:
                    highlight = self.create_highlight(res['BBOX'][0], res['BBOX'][1], res['BBOX'][2], res['BBOX'][3], {
                        "author": "COISearchEngine",
                        "contents": res['TAG']
                    })
                    self.add_highlight_to_page(highlight, page, pdf_output)
            pdf_output.addPage(page)
    
        output_stream = open(filepath_mark, "wb")
        pdf_output.write(output_stream)
        output_stream.close()
        file_input.close()
    
    def exportResults(self, filename_result=''):
        """ Export serach results into .xlsx file
            
        :param folderpath_result: Folderpath of results folder
        :type folderpath_result: str
        """   
        
        # Update folderpath 
        if not filename_result:
            filename_result = self.props['filename_result']
        filepath_result = os.path.join(self.props['folderpath_result'], filename_result)
            
        print('Export results to excel file.')
        df = pd.DataFrame(self.results)
        df['PAGE'] = df['PAGE'] + 1
        df = df.drop(['HITNUM', 'BBOX'], axis=1)
        df.to_excel(filepath_result, index=False)

    def deleteTmp(self):
        """ Delete tmp folder 'tmpdir'
        """   
        
        # Delete teporary directory tmpdir
        if os.path.exists("tmpdir"):
            shutil.rmtree('tmpdir')
            
##############################################################
if __name__ == '__main__':
    
    print('------------------------- Starting COISearchEngine -------------------------')
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--filepath_seetings", help="Filepath to the seetings.yml file.", type=str, default='settings.yml')
    args = parser.parse_args()

    # Create DocSearch
    docS = DocSearch(settingsfilepath=args.filepath_seetings)
    
    # Merge pdf files
    docS.merge()
    
    # Extract text from merged pdf file
    docS.extractPDFText()
    
    # Search tags in merged pdf file
    docS.searchTags()
    
    # Highlight results in pdf file
    docS.markResults()
    
    # Export results into .xlsx file
    docS.exportResults()
    
    # Delete teporal folder 'tmpdir'
    docS.deleteTmp()
    
    print('------------------------- EndFinished COISearchEngine -------------------------')
    
