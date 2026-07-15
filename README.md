# PixelTravelMap

PixelTravelMap 是一个离线旅行地图生成工具。它可以把旅行计划转换成结构化行程数据，并生成可直接打开的交互式 HTML 地图和 SVG 行程海报。

项目不依赖后端服务，也不需要 API key。生成的 HTML 和 SVG 文件可以直接在浏览器中打开，适合用于旅行前查看路线、给同行朋友分享每日行程，或在旅行结束后整理记录。

## 在线 Demo

- [在线创建器：上传 Word / 粘贴行程生成地图](https://leoxin99.github.io/PixelTravelMap/dist/builder.html)
- [意法瑞 8 日自驾 HTML 地图](https://leoxin99.github.io/PixelTravelMap/dist/italy_france_switzerland_demo.html)
- [意法瑞 8 日自驾 SVG 海报](https://leoxin99.github.io/PixelTravelMap/dist/italy_france_switzerland_demo_poster.svg)
- [日本关西城市旅行 HTML 地图](https://leoxin99.github.io/PixelTravelMap/dist/japan_kansai_demo.html)
- [北京亲子游 HTML 地图](https://leoxin99.github.io/PixelTravelMap/dist/beijing_family_demo.html)

## 功能

- 根据行程数据生成交互式 HTML 地图
- 使用经纬度展示 POI、路线、城市 detail view、比例尺和段间距离
- 查看完整日程、地点详情、来源信息和导航链接
- 在 HTML 页面内下载三类 SVG poster：
  - 总行程 poster
  - 每日行程 poster
  - 旅行记录 poster
- 在浏览器中记录全程备注、每日备注和地点备注
- 支持在创建器中上传 `.docx` 行程或粘贴自然语言行程
- 支持从自然语言 + 坐标的文本输入生成新地图
- 提供本地校验脚本，检查 JSON、HTML 和 SVG artifact

## 快速开始

需要 Python 3.10 或以上版本，无需安装第三方依赖。

```powershell
git clone git@github.com:leoxin99/PixelTravelMap.git
cd PixelTravelMap
python scripts/check_project.py
```

生成一个示例地图：

```powershell
python scripts/generate_map.py --input examples/inputs/italy_france_switzerland_self_drive.txt --output dist/italy_france_switzerland_demo.html --dump-json dist/italy_france_switzerland_demo.json --poster-svg dist/italy_france_switzerland_demo_poster.svg
```

生成后打开：

```text
dist/italy_france_switzerland_demo.html
dist/italy_france_switzerland_demo_poster.svg
```

## 使用自己的行程

### 在线创建

打开 [PixelTravelMap 创建器](https://leoxin99.github.io/PixelTravelMap/dist/builder.html)，可以：

1. 上传 `.docx` 行程文档，或把旅行计划粘贴到文本框。
2. 点击“解析行程”，检查自动生成的草稿。
3. 为每个地点补齐 `lat`、`lon`、`city` 和 `country`。
4. 点击“生成预览”，下载 JSON、HTML 地图或 SVG poster。

创建器不会联网查询坐标；如果 Word 文档里没有坐标，需要手动补充。

### 本地命令

自定义行程可以使用“自然语言 + 坐标”的文本格式。每个地点需要提供 `lat`、`lon`、`city`、`country`、`category` 和 `duration`。

示例：

```text
标题：日本东京 3 日亲子游
日期：2026-07-01 到 2026-07-03
交通：public-transit

Day 1：东京塔和城市观景
- 东京塔 (lat:35.6586, lon:139.7454, city:Tokyo, country:JP, category:landmark, duration:90)
- 六本木之丘 (lat:35.6605, lon:139.7292, city:Tokyo, country:JP, category:viewpoint, duration:120)
```

运行：

```powershell
python scripts/generate_map.py --input examples/inputs/tokyo_coordinate_trip.txt --output dist/tokyo_coordinate_demo.html --dump-json dist/tokyo_coordinate_demo.json --poster-svg dist/tokyo_coordinate_demo_poster.svg
```

支持的 `category`：

```text
landmark, museum, food, hotel, nature, transit, shopping, experience, viewpoint
```

## HTML 页面内的 Poster 和备注

打开生成的 HTML 后，可以在右侧 `Poster 工具` 中下载：

- 总行程 poster：适合旅行前整体了解路线
- 每日行程 poster：适合旅行前一天发给同行朋友
- 旅行记录 poster：适合旅行结束后整理回顾

页面内还可以填写：

- 全程备注
- 当前 Day 备注
- 当前地点备注

这些备注保存在当前浏览器的 `localStorage` 中，不会修改原始 JSON，也不会上传到任何服务器。

## 项目结构

```text
PixelTravelMap/
  pixel_travel_map/      # 解析、校验和渲染逻辑
  scripts/               # 命令行工具
  examples/              # 示例输入和期望 JSON
  schemas/               # itinerary JSON schema
  dist/                  # 示例 HTML / JSON / SVG artifact
  docs/                  # 补充文档
```

## 常用命令

校验行程 JSON：

```powershell
python scripts/validate_trip.py examples/expected/italy_france_switzerland_self_drive.json
```

检查生成的 HTML 或 SVG：

```powershell
python scripts/check_artifact.py dist/italy_france_switzerland_demo.html
python scripts/check_artifact.py dist/italy_france_switzerland_demo_poster.svg
```

运行完整项目检查：

```powershell
python scripts/check_project.py
```

重新生成在线创建器：

```powershell
python scripts/build_builder.py --output dist/builder.html
```

## 注意事项

- 地图距离基于经纬度计算，为直线近似距离，不等同于实际驾车或步行距离。
- 自定义地点需要手动提供坐标，项目不会在线查询地理位置。
- 创建器支持 `.docx`，不支持旧版 `.doc`、PDF 或扫描图片。
- HTML 和 SVG artifact 均为离线文件，不依赖外部脚本或样式。
- 浏览器中的旅行备注只保存在本机当前浏览器中。

## License

MIT
