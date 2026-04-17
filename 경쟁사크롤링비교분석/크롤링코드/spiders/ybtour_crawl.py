import scrapy
from urllib.parse import parse_qs
import requests
import pandas as pd


class YbtourSpider(scrapy.Spider):
    name = 'ybtour'
    results = []

    def start_requests(self):
        url = 'http://www.ybtour.co.kr/product/locList.do?menu=pkg&did=211'
        yield scrapy.Request(url)

    def parse(self, response):
        pids = response.xpath('//select[@id="codeAreaDetail2"]/option/@data-pid').extract()
        dids = response.xpath('//select[@id="codeAreaDetail2"]/option/@data-did').extract()

        for pid, did in zip(pids, dids):
            url = 'http://www.ybtour.co.kr/product/incLocList.do?menu=pkg&loc=294&pid={pid}&did={did}&pdtSort=&startRow=1&endRow=100'
            url = url.format(pid=pid, did=did)
            yield scrapy.Request(url, callback=self.parse_detail1)

    def parse_detail1(self, response):
        a_s = response.xpath('//ul[@class="goods_list"]/li/div[1]//a/@href').extract()
        for a in a_s:
            did = parse_qs(a)['did'][0]
            goodsCd = parse_qs(a)['goodsCd'][0]
            url = 'http://www.ybtour.co.kr/product/unitMonList.do?menu=pkg&goodsCd={}&compId=1&year=2019&month=03&startDate=&evRsrvYn=&loc=&pid=&did={}&compareBtnYn='.format(goodsCd, did)
            yield scrapy.Request(url, callback=self.parse_detail2)

    def parse_detail2(self, response):
        did = parse_qs(response.url)['did'][0]
        상품번호 = response.xpath('//tbody/tr/td[4]/a/@href').extract()
        상품번호 = [parse_qs(i)['evCd'][0] for i in 상품번호]
        제목 = response.xpath('//tbody/tr/td[4]/a/text()').extract()
        여행기간 = response.xpath('//tbody/tr/td[5]/text()').extract()
        항공 = response.xpath('//tbody/tr/td[3]/text()').extract()
        항공 = [i for i in 항공 if i.strip()]
        가격 = response.xpath('//tbody/tr/td[6]/text()').extract()
        가격 = [i for i in 가격 if i.strip()]
        td7 = response.xpath('//tbody/tr/td[7]')
        출발확정여부 = []
        for i in td7:
            if i.xpath('span[2]/text()').extract_first() == '[출발확정]':
                출발확정여부.append('출발확정')
            else:
                출발확정여부.append('미정')
        프리미엄여부 = ['프리미엄'] if response.xpath('//tbody/tr/td[4]/a/span[1]/text()').extract() else ['일반']
        프리미엄여부 = 프리미엄여부 * len(상품번호)
        for prd_no, subj, duration, airline, price, is_start, is_preminum in zip(상품번호, 제목, 여행기간, 항공, 가격, 출발확정여부, 프리미엄여부):
            if is_start == ('출발확정','미정'):
                r = requests.get('http://www.ybtour.co.kr/product/detailPackage.do?menu=pkg&did={}&evCd={}'.format(did, prd_no))
                hxs = scrapy.Selector(text=r.text)
                예약인원 = hxs.xpath('//span[text()="예약 "]/following-sibling::span[1]/text()').extract_first()
                data = {'상품번호': prd_no, '제목': subj, '여행기간': duration, '항공': airline, '가격': price, '출발확정여부': is_start, '예약인원': 예약인원, '등급': is_preminum}
            else:
                data = {'상품번호': prd_no, '제목': subj, '여행기간': duration, '항공': airline, '가격': price, '출발확정여부': is_start, '등급': is_preminum}
            self.results.append(data)

    def close(self, reason):
        df = pd.DataFrame(self.results)
        df.to_excel('결과_노랑3월.xlsx')
        




