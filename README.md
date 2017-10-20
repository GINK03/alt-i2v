# Alternative Implementation Of Illustration2Vec Ver2.

## Illustration2Vecの概要
- 画像をタグ等の特定の特徴量に従ってベクトル化できる
- このベクトルとは通常画像分類で用いられるsoftmaxなどのマルチクラスではなく、softprobの(\*1)問題として捉えることができる

\*1 softprobはxgboostの用語でありますが、各クラスに該当するものが、その確率値を返すものです  

## VGG16の転移学習
VGG16の評価モデルはよくチューニングされており、別段何かしなくても良いパフォーマンスが出せます  
そのため、VGG16の評価モデルを転移学習することでそのチューニングされた良い状態を保存しつつ、softprobに該当する部分を付け足すことで、illustration2vecに該当する機能を付与させます

## モデル図

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

## 
