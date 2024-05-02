#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author  : ellenbboe

import os
import jieba
from imageio import imread
from wordcloud import WordCloud


class Generator:
    def __init__(self, words,stopwords, color, font, image=None):
        super(Generator, self).__init__()
        self.words = words
        self.stopwords = stopwords
        self.color = color
        self.font = font
        self.image = image

    def generate(self):
        with open(self.stopwords, encoding='utf-8') as f_stop:
            f_stop_text = f_stop.read()
            f_stop_seg_list = f_stop_text.splitlines()

        # 读入文本内容
        text = open(self.words, encoding='utf-8').read()
        # 中文分词
        seg_list = jieba.cut(text, cut_all=False)

        # 把文本中的stopword剃掉
        my_word_list = []

        for my_word in seg_list:
            if len(my_word.strip()) > 1 and not (my_word.strip() in f_stop_seg_list):
                my_word_list.append(my_word)

        my_word_str = ' '.join(my_word_list)

        # 字体不要包含中文，否则会报错！
        font_path = self.font

        if self.image:
            wc = WordCloud(
                font_path=font_path,
                background_color=self.color,
                mask=imread(self.image),
            )
        else:
            wc = WordCloud(
                font_path=font_path,
                background_color=self.color,
                random_state=1024,
                width=1920,
                height=1080,
            )
        try:
            wc.generate(my_word_str)
            wc.to_file('images/output.png')
        except Exception as e:
            print(e)


if __name__ == '__main__':
    path = os.getcwd()
    image_generator = Generator(words="./input.txt",
                                stopwords="./stopwords.txt",
                                font="./Normal.otf",
                                color="white")#,
                                #image="./shape.jpeg")
    image_generator.generate()
