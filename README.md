# Alternative Implementation Of Illustration2Vec Ver2.

## Alternative Illustration2Vec Ver2の概要
- 画像をタグ等の特定の特徴量に従ってベクトル化できる
- このベクトルとは通常画像分類で用いられるsoftmaxなどのマルチクラスではなく、softprobの(\*1)問題として捉えることができる

### Version2の改善、変更点
- Ver1に比べて探索的であって割とひどいコードを修正して、わかりやすく変えました
- 150x150の画像のサイズから、224x224にスケールアップしました
- BatchNormalizationだけでなく、DropOutも併用してネットワークのスパース性を高めました
- Msgpackを用いたKVSをやめて、ただのPickleで画像のシリアライズをする様になりました
- Keras V2のインターフェースに合わせました

\*1 softprobはxgboostの用語でありますが、各クラスに該当するものが、その確率値を返すものです  

## VGG16の転移学習
VGG16の評価モデルはよくチューニングされており、別段何かしなくても良いパフォーマンスが出せます  
そのため、VGG16の評価モデルを転移学習することでそのチューニングされた良い状態を保存しつつ、softprobに該当する部分を付け足すことで、illustration2vecに該当する機能を付与させます

## モデル図  
毎回気持ちですみません（しかし、なんらかの活性化関数の新規のものの提案というスタイルではないので、雑でいいという思いがあります）  
<div align="center">
  <img src="https://user-images.githubusercontent.com/4949982/31811430-7ee4de0a-b5ba-11e7-8bc7-d6749cb4e9cf.png">
</div>
<div align="center"> 図1. モデルのイメージ </div>

## 転移学習時のネットワーク設計
今回は過去最大の5000次元を予想するというタスクであったので、全結合層をReLuで結合していきます  
前回はBatchNormalizationのみでやったのですが、これだけを用いうることに少し不安があったので、DropOutを30%のデータを入れるようにしました  
ReLu, DropOutともネットワークを疎結合にする役割が期待できますので、ネットワークの意味のクラスタが獲得しやすくなると期待できます  

## オプティマイザと損失関数
これ系のタスクではAdamかSGDが良い成績をいつも収めることが期待されていますので、何も考えず、Adamで決め打ちです  
- オプティマイザ、Adam : LearningRate 0.001
- 損失関数、BINARY CROSS ENTROPY

## 使ったデータセット
Safebooruさんからダウンロードさせていただきました  
タグとURLと画像の三つの情報を保存し、学習用のデータセット1,500,000枚、テスト様に20,000枚用意します  

## データがメモリに乗り切らないときに使ったアプローチ
メモリに乗らないときは、最近いつも使うのですが、データセットを分割読み込みまします  
ソフトウェア工学者にとっては一般的なアプローチですが、Epochと対応させて学習すると、なんとかスケジューリングできます(ちゃんとKerasのインターフェースの中にはgeneratorというデータセットを切り出す仕組みがありますが、私はこれを操作が複雑になりすぎると感じているであまり用いていません)  

具体的には、15000枚の画像をオンメモリに保持 -> 1Epoch回す -> 別の150000枚の画像をオンメモリに保持 -> 1Epoch回す -> ...
  
ということを続けていきます

全てが一回のみスキャンされます

## 転移学習の例

### 前処理
make_datapairディレクトリ内のmake_datapair.pyを"--make_tag_index"オプションをつけて実行すると、特定のディレクトリの内部の画像とタグ情報に対して、よく頻出するタグ5000個に対して、タグとそのインデックスを記述します  

make_dataset.pyを"--make_pair"のオプションをつけて実行することで、実行することで、タグとインデックスをもとに、画像のベクトル情報 Xとそのタグ情報をベクトル化した情報yのペアを作ります。一つの画像に対して、Piar(X,y)となる情報をpickle形式のファイルで出力します  

### 学習
alt_i2v_V2.pyに"--train"オプションをつけて実行することで、学習します。15000枚の画像のデータセットをラウンドロビンで切り替えながら学習しますが、メモリ64GByteマシンの基準でやっていますので、必要に応じて、サイズを小さくするか、ランダムサンプルに切り替えるか、Epoch数を変化させるなどすると良いでしょう  

### 予想
alt_i2v_V2.pyに"--pred"オプションをつけて実行することで予想が可能です  


## 評価
定量的なMSEの他に、定性的なみんなが好きそうな結果を載せておきます  
結果は概ね、良好で、画像識別は本当に今や簡単になりましたね、という印象があります  

<div align="center">
  <img width="450px" src="https://user-images.githubusercontent.com/4949982/31794222-77a9fa70-b55c-11e7-8b77-b13f738c7301.png">
</div>

<div align="center" >
  <img width="350px" src="https://user-images.githubusercontent.com/4949982/31794577-bb07323c-b55d-11e7-9e93-4fb761bda917.png">
</div>

<div align="center">
  <img width="450px" src="https://user-images.githubusercontent.com/4949982/31794618-e59cd1fa-b55d-11e7-8d4c-22b1a5b20230.png">
</div>

<div align="center">
  <img width="350px" src="https://user-images.githubusercontent.com/4949982/31794847-9c2fdf98-b55e-11e7-84ea-7f6c8551bbf0.png">
</div>


<div align="center"">
  <img width="450px" src="https://user-images.githubusercontent.com/4949982/31795198-df56f788-b55f-11e7-924b-01d42f5f4315.png">
</div>

<div align="center">
  <img width="350px" src="https://user-images.githubusercontent.com/4949982/31809809-4e4b1ff8-b5b4-11e7-8d58-074804960a32.png">
</div>

## KPI予想としてのIllustration2Vec
[Practical Lessons from Predicting Clicks on Ads at Facebook](https://research.fb.com/wp-content/uploads/2016/11/practical-lessons-from-predicting-clicks-on-ads-at-facebook.pdf)という論文があります  

趣旨としては、テキストや画像やなんらかを特徴量の集合としてみなして、CTR予想などのKPI予想問題を行う際、特徴量が極めて高次元である際、アルゴリズム（この場合、勾配ブースティングの木の出力値）を特徴量とすることで、これを元にLinear Regressionをかけることで、より実践的な速度で、より高精度で予想できるという趣旨でした  

勾配ブースティングはそのアルゴリズムから残渣となる誤差を最小化する様に特徴量を選択しますが、例えば、これがIllustration2Vecの出力次元値ではどうでしょうか。アルゴリズムが自動で獲得した粒度の特徴量ではないですが、同様の圧縮された特徴量の空間と見做すことができます。(LDA的な自動でクラスタを獲得させる方法も筋が良さそうです)  

データが十分に手元にないので、検証は今現在、簡単に行えそうにはありませんが、できそうなことなのでいずれチャレンジしたいと考えています  

## コード
こちらからダウンロード可能です  
[https://github.com/GINK03/alt-i2v](https://github.com/GINK03/alt-i2v)

## ライセンス
MIT

