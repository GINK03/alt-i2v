
# Safebooruを使用した画像とタグのスクレイピング（safebooru_datasetgenerator.py）  

アメリカのアニメ画像検索エンジンであるSafebooruから画像と画像のタグをスクレイピングするプログラムです。  
Danbooruのスクレイパーを改修し、Safebooruに対応させました。  

### 使用方法  
以下のコマンドで実行します。  

> python3 safebooru_datasetgenerator.py --mode scrape  

<br />

実行すると、画像とタグ情報のテキストがそれぞれ以下のディレクトリに保存されます。  

◾️　画像    
./img直下にjpg形式で保存   
<br />

◾️ タグ情報  
./img直下にtxt形式で保存  
<br />

また、画像が存在し、スクレイピングが終了したものについては、./finished直下に画像IDの名前でファイルが出力されます。  
ファイルの中には「f」が記載されています。  
<br />

### DanbooruとSafebooruの違い  
DanbooruとSafebooruでは文書構造に違いがあり、画像のソースと画像タグの取得元は以下の通り変更しました。  

◾️Danbooru (旧)  
画像のソース： sectionタグ（id: image-container）の中のimgタグ内の属性「src」  
画像タグ： sectionタグ（id: image-container）の中のimgタグ内の属性「data-tags」
<br />

◾️Safebooru  （新）  
画像のソース： imgタグ（id: image）の属性「src」  
画像タグ： imgタグ（id: image）の属性「alt」  

