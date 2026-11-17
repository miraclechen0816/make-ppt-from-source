# 图片转可编辑

## 转换的职责

代理阅读已经补齐配图的最终成图，结合原始文案建立对象清单。内置工具把这份清单写成原生PowerPoint对象。图片识别、内容校对与对象定位由当前代理完成，脚本负责确定性的文件构建。

普通标题、正文、数字、坐标标签逐行建立文字对象；基础面板、线条、规则图形、表格和有准确数据的图表采用原生对象。照片、截图、复杂视觉和具有特殊造型的艺术字保留为独立高清图片。每个对象保留源图中的位置、比例、顺序及必要的遮挡关系。

## 安装与执行

Python 3.10或更高版本。使用任务本地虚拟环境安装技能目录的 `requirements.txt`。渲染在Windows使用已安装的PowerPoint；其他平台使用LibreOffice，并安装PyMuPDF。

```text
python -m pip install -r <skill-root>/requirements.txt
python <skill-root>/scripts/build_decks.py editable_manifest.json --out-dir outputs --mode both
python <skill-root>/scripts/inspect_pptx.py outputs/project_editable.pptx --out outputs/object_audit.json
python <skill-root>/scripts/render_deck.py outputs/project_editable.pptx --out review/editable
python <skill-root>/scripts/render_deck.py outputs/project_image.pptx --out review/image
```

每次构建使用新输出目录或新的文件前缀。工具保留已有文件和渲染工作目录。

## 对象清单

坐标使用 `canvas` 定义的逻辑画布，默认1920×1080。最终页面图片与逻辑画布保持相同比例，原始像素独立保存。所有文件路径相对于清单所在目录。

```json
{
  "title": "项目展示", "file_stem": "project", "canvas": [1920, 1080],
  "width_inches": 13.333333, "language": "zh-CN",
  "slides": [{
    "title": "项目标题", "image": "final_slides/slide_001.png",
    "background": {"color": "F5F5F4"},
    "notes": "对应最终页面的讲者备注。",
    "elements": [
      {"id": "title", "kind": "text", "box": [100, 90, 1500, 130],
       "text": "项目标题", "font": "Microsoft YaHei", "font_size": 96,
       "bold": true, "color": "17374A"},
      {"id": "photo", "kind": "image", "box": [1050, 290, 760, 620],
       "path": "image_assets/case.png", "fit": "cover"}
    ]
  }]
}
```

每页 `image` 是完整定稿成图，供图片版使用。可编辑版使用单独的背景与对象清单。纹理、渐变或场景背景先准备为无字背景，写成 `background: {"image": "backgrounds/page_001.png", "text_free": true}`。实际源图中的普通文字需要从背景中移除，再以原生文字还原。脚本会拒绝直接把完整原图用作可编辑背景。

## 元素字段

| 类型 | 必需字段 | 常用选项 |
|---|---|---|
| `text` | `id`, `kind`, `box`, `text` | `font_size`、`font`、`color`、`bold`、`italic`、`underline`、`align`、`vertical_align`、`rotation` |
| `shape` | `id`, `kind`, `box` | `shape`为rect、roundRect、ellipse、triangle、rightArrow、downArrow或chevron；`fill`、`stroke`、`line_width` |
| `line` | `id`, `kind`, `points` | `points`为坐标对数组，折线逐段写入；`color`、`line_width`、`end_arrow` |
| `image` | `id`, `kind`, `box`, `path` | `fit`为contain或cover；直接嵌入原图，不缩小素材像素 |
| `table` | `id`, `kind`, `box`, `rows` | `column_widths`、`row_heights`、`header_fill`、`header_color`；`merges`为`[row,col,rowspan,colspan]`列表，被覆盖的单元格内容留空 |
| `chart` | `id`, `kind`, `box`, `categories`, `series` | `chart_type`为column、bar、line、pie或doughnut；series含name与values，采用准确数据 |

`box`为`[x,y,w,h]`。`font_size`和`line_width`使用逻辑画布像素，构建时按最终幻灯片尺寸换算。对象按`z`从低到高排列，同一层按清单顺序绘制；默认`z=0`。每个ID在一页中唯一。

一行内的不同样式可用 `runs: [{"text": "核心", "bold": true}, {"text": "信息"}]`。多段文字可用`paragraphs`，但需要分别调整位置的源图行优先写成独立文字对象。保持准确换行、字重、单位和标点，按源图测量字体与文字框。

## 画质与编辑性回看

- 图片版每页保持一个完整图片对象；可编辑版逐项验证文字、表格、图形及图表，检查复杂视觉图片可独立替换。
- 用实际PowerPoint或LibreOffice渲染，逐页比较边界、对齐、字号、换行、连线、图表数值、裁切和层级。观察到的差异在对象清单中定向修正，再输出新版本。
- 通过`inspect_pptx.py`记录对象类型、可提取文字、素材像素及哈希，核对当前PPTX与内嵌图表工作簿的作者信息。字号、字体差异以实际渲染为准。
- 照片、截图和事实图表复用已核实素材；大图使用满足最终占位需求的原生像素。复杂图像保持完整主体，外部标题、图例和标签分别处理。
- 两份PPT的最终文案、页序、配图和备注一致，全部必需配图位置已核验。输出作者与最后修改者默认为“用户”。
