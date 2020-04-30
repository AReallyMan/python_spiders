# coding: utf-8
from aip import AipNlp


class SentimentAnalysis:
    def __init__(self):
        self.client = AipNlp('17726220', 'Gz2Qiz7braK5a21agrGQB2gt', 'pQgtpqmKN5iX2DewNwT1y7Z8kbEfXoG6')

    def analysis(self, title):
        # .encode(‘utf - 8’).decode(‘unicode - escape’)
        # urllib.unquote(datas[0].encode('unicode-escape').decode('string_escape'))

        title = title.encode('raw-unicode-escape').decode("utf-8","ignore")
        title = title if len(title) < 60 else title[0:60]
        sentimentResult = self.client.sentimentClassify(title)

        sentiment = sentimentResult['items'][0]['sentiment']
        if sentiment == 0:
            type = '负向'
        elif sentiment == 2:
            type = '正向'
        elif sentiment == 1:
            type = '中性'
        else:
            type = '未知'
        return type


if __name__ == "__main__":
    sent = SentimentAnalysis()
    title = "百度快照"


