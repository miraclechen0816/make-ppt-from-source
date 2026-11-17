"""Exercise actual PPTX structure, media preservation and metadata behavior."""
from pathlib import Path
from io import BytesIO
import hashlib
import json
import runpy
import unittest
import uuid
import zipfile
from PIL import Image, ImageDraw
from lxml import etree
from pptx import Presentation

__author__ = '用户'
ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / 'skills/make-ppt-from-source/scripts'
BUILD = runpy.run_path(str(SCRIPTS/'build_decks.py'), run_name='build_module')['build']
INSPECT = runpy.run_path(str(SCRIPTS/'inspect_pptx.py'), run_name='inspect_module')['inspect']
GRID = runpy.run_path(str(SCRIPTS/'make_style_grid.py'), run_name='grid_module')['make_grid']


class DeckBuildTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Preserve test runs instead of recursively deleting temporary folders.
        cls.work = ROOT / 'test_outputs' / uuid.uuid4().hex[:12]
        cls.work.mkdir(parents=True)
        Image.new('RGB', (1920,1080), '#f5f5f4').save(cls.work/'source.png')
        icon = Image.new('RGBA', (512,512), (0,0,0,0))
        draw = ImageDraw.Draw(icon)
        draw.rounded_rectangle((25,25,487,487), radius=100, fill='#27aef5')
        icon.save(cls.work/'icon.png')
        cls.manifest = {'title':'构建器自检', 'file_stem':'self_check', 'canvas':[1920,1080], 'slides':[{
            'title':'从资料到作品', 'image':'source.png', 'background':{'color':'F5F5F4'},
            'notes':'同一备注写入两份交付文件。', 'elements':[
                {'id':'title','kind':'text','box':[100,70,1500,130], 'text':'从资料到作品','font_size':96,'bold':True,'color':'17374A'},
                {'id':'subtitle','kind':'text','box':[100,220,1400,80], 'runs':[{'text':'5种风格','bold':True},{'text':' · 两份PPT'}], 'font_size':44},
                {'id':'panel','kind':'shape','box':[90,350,790,600], 'shape':'roundRect','fill':'EAF7FE'},
                {'id':'arrow','kind':'line','points':[[140,840],[350,840],[350,895]],'color':'27AEF5','line_width':5,'end_arrow':True},
                {'id':'image','kind':'image','box':[610,680,180,180], 'path':'icon.png','fit':'contain'},
                {'id':'table','kind':'table','box':[130,395,700,220], 'rows':[['输出','数量'],['风格预览','5'],['PPT版本','2']], 'font_size':38},
                {'id':'chart','kind':'chart','box':[990,350,790,610], 'categories':['风格','PPT'], 'series':[{'name':'数量','values':[5,2]}], 'chart_type':'column'}]}]}
        cls.path = cls.work/'manifest.json'
        cls.path.write_text(json.dumps(cls.manifest,ensure_ascii=False),encoding='utf-8')
        cls.audit = BUILD(cls.path,cls.work/'valid')

    def test_native_objects_and_matching_notes(self):
        editable=Presentation(self.work/'valid/self_check_editable.pptx')
        image=Presentation(self.work/'valid/self_check_image.pptx')
        self.assertEqual(len(image.slides[0].shapes),1)
        self.assertEqual(int(image.slides[0].shapes[0].shape_type),13)
        self.assertTrue(any(shape.has_table for shape in editable.slides[0].shapes))
        charts=[shape.chart for shape in editable.slides[0].shapes if shape.has_chart]
        self.assertEqual(list(charts[0].series[0].values),[5.0,2.0])
        self.assertIn('从资料到作品',[s.text for s in editable.slides[0].shapes if s.has_text_frame])
        self.assertEqual(editable.slides[0].notes_slide.notes_text_frame.text,image.slides[0].notes_slide.notes_text_frame.text)

    def test_metadata_and_original_pixels(self):
        audit=INSPECT(self.work/'valid/self_check_editable.pptx')
        self.assertEqual(audit['metadata'],{'author':'用户','last_modified_by':'用户'})
        self.assertEqual(audit['embedded_workbooks'][0]['author'],'用户')
        self.assertEqual(audit['embedded_workbooks'][0]['last_modified_by'],'用户')
        icon_hash=hashlib.sha256((self.work/'icon.png').read_bytes()).hexdigest()
        self.assertTrue(any(m['sha256']==icon_hash and m['native_px']==[512,512] for m in audit['media']))

    def test_existing_outputs_are_preserved(self):
        file=self.work/'valid/self_check_editable.pptx'
        before=file.read_bytes()
        with self.assertRaises(FileExistsError): BUILD(self.path,self.work/'valid')
        self.assertEqual(file.read_bytes(),before)

    def test_metadata_qname_prefixes_remain_bound(self):
        with zipfile.ZipFile(self.work/'valid/self_check_editable.pptx') as package:
            core=etree.fromstring(package.read('docProps/core.xml'))
            for element in core.iter():
                value=element.get('{http://www.w3.org/2001/XMLSchema-instance}type')
                if value and ':' in value:
                    self.assertIn(value.split(':',1)[0],element.nsmap)

    def test_flat_source_cannot_be_editable_background(self):
        manifest=json.loads(json.dumps(self.manifest))
        manifest['slides'][0]['background']={'image':'source.png','text_free':True}
        path=self.work/'bad_background.json'
        path.write_text(json.dumps(manifest),encoding='utf-8')
        with self.assertRaises(ValueError): BUILD(path,self.work/'bad_background')

    def test_duplicate_ids_are_rejected(self):
        manifest=json.loads(json.dumps(self.manifest))
        manifest['slides'][0]['elements'][1]['id']='title'
        path=self.work/'bad_ids.json'
        path.write_text(json.dumps(manifest),encoding='utf-8')
        with self.assertRaises(ValueError): BUILD(path,self.work/'bad_ids')

    def test_nine_grid_order_and_metadata(self):
        paths=[]
        for index in range(9):
            path=self.work/f'grid_input_{index}.png'
            Image.new('RGB',(320,180),(index*20,60,110)).save(path)
            paths.append(path)
        output=self.work/'grid.png'
        GRID(paths,output,320,12)
        with Image.open(output) as image:
            self.assertEqual(image.info['Author'],'用户')
            for index in range(9):
                self.assertEqual(image.getpixel((12+index%3*332+160,12+index//3*192+90)),(index*20,60,110))
        with self.assertRaises(ValueError): GRID(paths[:8],self.work/'eight.png')


if __name__=='__main__':
    unittest.main()
