# -*- coding: utf-8 -*-
"""cnn_pytorch_tutorial.ipynb
"""function2

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1MWxmsqAzZrx8F5k4PlzXeHEOoeUZ-fm-

参照元：https://pytorch.org/tutorials/beginner/blitz/cifar10_tutorial.html

ソースコードは全てtutorialのもの
注釈は田儀のメモ

tutorialの問題設定
    データセット：CIFAR10　(10 class, 3x32x32)


画像分類の手順
    torchvisionを使ってCIFAR10データセットをロード＆正規化（torchvisionはMNISTなどよくあるデータセットをダウンロードするもの）
    CNN: Convolutional Nural Networkを定義
    lossを定義
    training dataで学習
    testデータでテスト

note
    なんでチャンネル数を増やしているんだろう　各チャンネルは何を意味するのか？：チャンネル＝カーネル、特徴を表すとも言えるかもしれない
    チャンネルを増やすって具体的にどういう操作？：つまり特徴を表現できる場所をいっぱい用意してあげる感じか
    畳み込み＞全結合という流れなら、畳み込みの意味は？カーネル/チャンネルを学習する＝画像の概念を学習する感じ、それを元に全結合で、その情報を解釈してクラス分類って感じか
    → 考えがあってるか？oracleの本に目を通してみたい

    実際に読み込まれるデータはどういう形？　←これが知りたいことは、conv2dのinputのshape。
    input, outputのshapeに関してはdocumentation: https://pytorch.org/docs/stable/generated/torch.nn.Conv2d.html

    学習の手順？ミニバッチごとの学習？全体のデータ数がいくつで、教師データがいくつで、どういう学習？
    →教師データの数：50000、ミニバッチ：４　なので50000/4=12500 epochの学習　これを２回やってるな

    まってそしたらフィルタに対してどうやってバックプロパゲーション？
    →ここは詳細なことなのでまた調べる。
"""

# load and normalize cifar10
import torch
import torchvision
# torchvision.transformsモジュールで使用できる一般的な画像変換 リサイズや切り抜きなど
import torchvision.transforms as transforms

"""
https://teratail.com/questions/280822

"""

# Composeでチェインできる（一連の処理をまとめて記述できる）
transform = transforms.Compose(
    [transforms.ToTensor(), # PIL画像からTensorに変換し[0, 1]の範囲に変換
     transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))]) # 範囲を[0, 1]から[-1, 1]に変換 
     # https://teratail.com/questions/280822

batch_size = 4

trainset = torchvision.datasets.CIFAR10(root='./data', train=True,
                                        download=True, transform=transform)
trainloader = torch.utils.data.DataLoader(trainset, batch_size=batch_size,
                                          shuffle=True, num_workers=2)

testset = torchvision.datasets.CIFAR10(root='./data', train=False,
                                       download=True, transform=transform)
testloader = torch.utils.data.DataLoader(testset, batch_size=batch_size,
                                         shuffle=False, num_workers=2)

classes = ('plane', 'car', 'bird', 'cat',
           'deer', 'dog', 'frog', 'horse', 'ship', 'truck')

print(trainset)

print(testset)

# training画像をいくつか可視化
import matplotlib.pyplot as plt
import numpy as np

# functions to show an image
def imshow(img):
    img = img / 2 + 0.5     # unnormalize
    npimg = img.numpy()
    plt.imshow(np.transpose(npimg, (1, 2, 0)))
    plt.show()


# get some random training images
dataiter = iter(trainloader)
images, labels = dataiter.next()

# show images
imshow(torchvision.utils.make_grid(images))
# print labels
print(' '.join(f'{classes[labels[j]]:5s}' for j in range(batch_size)))

# CNNの定義
import torch.nn as nn
import torch.nn.functional as F


class Net(nn.Module):
    def __init__(self):
        super().__init__()
        # 3 input image channel, 6 output channels, 5x5 square convolution kernel
        self.conv1 = nn.Conv2d(3, 6, 5) 
        self.pool = nn.MaxPool2d(2, 2)# Max pooling over a (2, 2) window
        self.conv2 = nn.Conv2d(6, 16, 5)
        # an affine operation: y = Wx + b
        self.fc1 = nn.Linear(16 * 5 * 5, 120) # 5*5 from image dimension # 16channels x 5width x 5hight
        self.fc2 = nn.Linear(120, 84)
        self.fc3 = nn.Linear(84, 10)

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = torch.flatten(x, 1) # flatten all dimensions except batch
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)
        return x


net = Net()

# 損失関数とoptimizerの定義
import torch.optim as optim

criterion = nn.CrossEntropyLoss()
optimizer = optim.SGD(net.parameters(), lr=0.001, momentum=0.9)

# training
for epoch in range(2):  # loop over the dataset multiple times

    running_loss = 0.0
    for i, data in enumerate(trainloader, 0):
        # get the inputs; data is a list of [inputs, labels]
        inputs, labels = data

        # zero the parameter gradients
        optimizer.zero_grad()

        # forward + backward + optimize
        outputs = net(inputs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        # print statistics
        running_loss += loss.item()
        if i % 2000 == 1999:    # print every 2000 mini-batches
            print(f'[{epoch + 1}, {i + 1:5d}] loss: {running_loss / 2000:.3f}')
            running_loss = 0.0

print('Finished Training')

# モデルの保存
PATH = './cifar_net.pth'
torch.save(net.state_dict(), PATH)

# test (一例)
dataiter = iter(testloader)
images, labels = dataiter.next()

# print images
imshow(torchvision.utils.make_grid(images))
print('GroundTruth: ', ' '.join(f'{classes[labels[j]]:5s}' for j in range(4)))
outputs = net(images)
_, predicted = torch.max(outputs, 1)

print('Predicted: ', ' '.join(f'{classes[predicted[j]]:5s}'
                              for j in range(4)))

# 全体に対してのテスト
correct = 0
total = 0
# since we're not training, we don't need to calculate the gradients for our outputs
with torch.no_grad():
    for data in testloader:
        images, labels = data
        # calculate outputs by running images through the network
        outputs = net(images)
        # the class with the highest energy is what we choose as prediction
        _, predicted = torch.max(outputs.data, 1)
        total += labels.size(0)
        correct += (predicted == labels).sum().item()

print(f'Accuracy of the network on the 10000 test images: {100 * correct // total} %')

# クラスごとの予測性能
# prepare to count predictions for each class
correct_pred = {classname: 0 for classname in classes}
total_pred = {classname: 0 for classname in classes}

# again no gradients needed
with torch.no_grad():
    for data in testloader:
        images, labels = data
        outputs = net(images)
        _, predictions = torch.max(outputs, 1)
        # collect the correct predictions for each class
        for label, prediction in zip(labels, predictions):
            if label == prediction:
                correct_pred[classes[label]] += 1
            total_pred[classes[label]] += 1


# print accuracy for each class
for classname, correct_count in correct_pred.items():
    accuracy = 100 * float(correct_count) / total_pred[classname]
    print(f'Accuracy for class: {classname:5s} is {accuracy:.1f} %')