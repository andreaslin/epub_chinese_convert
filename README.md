# epub_chinese_convert epub中文簡繁體轉換
Using [opencc](https://github.com/BYVoid/OpenCC) and [pyopencc](https://github.com/cute/pyopencc) to convert epub file between Chinese characters.

用[opencc](https://github.com/BYVoid/OpenCC)和[pyopencc](https://github.com/cute/pyopencc)來做epub格式的簡繁體中文轉換

## Installation 安裝
### opencc
Please refer to opencc [Installation-安裝](https://github.com/BYVoid/OpenCC#installation-安裝) page

## Usage 用法
### epub_chinese_convert
```
epub_convert_chinese.py [-h] -i INPUT_FILE [-o OUTPUT_FILE] -c CONFIG_OPTION [-v VERBOSE]
```

## Example 範例
```
python epub_chinese_convert.py -i my_book.epub -c s2tw
```

## Configurations 設定文件
Please refer to opencc [Configurations-配置文件](https://github.com/BYVoid/OpenCC#configurations-配置文件) page

## License 使用許可
MIT License

## Notes
  1. This script is created since http://epubconv.mobi/ can only take file under 10MB (Update - May 7, 2016: The site is down)
  2. No encoding check for the file; encoding is assume to be UTF-8

## TODO
  1. Deal with encoding
  2. Setup a website for online convert
