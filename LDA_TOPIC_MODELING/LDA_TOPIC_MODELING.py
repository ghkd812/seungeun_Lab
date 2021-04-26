import codecs
import re
import warnings
warnings.filterwarnings(action='ignore', category=UserWarning, module='gensim')
from gensim import corpora
import logging, gensim
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
from collections import Counter
from konlpy.tag import Kkma
from konlpy.tag import Twitter
from operator import itemgetter


stemming_keyword = ['여행','여행사','고객','다음','이번','마지막','머리','따분','우방','귀로','한국인',
                    '제가','다른','저희','모두','이드','다시','손발','여행객','페키','래서',
                    '해박','주신','사람','생각','정말','처음','우리','상품','취해','그동안','감사',
                    '집사람','여러가지','해돋이','국내','운영','기분','참좋은여행','낙산사','퇴직','정보',
                    '대해','전하','박찬미','마치','미리','마다','려니','느낌','직장','제주도','진행','정기','일정',
                    '정도','계속','9일','구매자','때문','하나','한번','주심','지난해','천적','감사','가이드','인솔']



# 명사분리 + 불용어 처리 함수
def tokenize(doc):
    post_tagger = Twitter()
    #p = re.compile("[^0-9]")
    noun_list = post_tagger.nouns(doc)
    final_noun_list =  [''.join(t) for t in noun_list if t not in stemming_keyword if len(t) > 1 if not t.isdigit()]
    return final_noun_list

# 텍스트에서 명사 분리하여 빈도 계산
def get_tags(text, ntags):
    spliter = Twitter()
    nouns = spliter.nouns(text)
    count = Counter(nouns)
    return_list = []
    for n, c in count.most_common(ntags):
        temp = {'tag': n, 'count': c}
        return_list.append(temp)
    return return_list

lda_main_keyword = []

case_keyword = ['동남아_CR','중국_CR','일본_CR','유럽_CR','대양주_CR','북미지역_CR']

#case_keyword = ['동남아']
a = 1
i = 0


# 메인 코드

for i in range(len(case_keyword)):
    sentences_vocab = []

    line = codecs.open("C:/Users/VGL_P17041/Documents/%s.txt" %case_keyword[i] , encoding='utf-8').read()

    sentences_vocab.append(tokenize(line))


    # document-term matrix 만들기
    print(get_tags(str(sentences_vocab),100))
    dictionary = corpora.Dictionary(sentences_vocab)
    corpus = [dictionary.doc2bow(text) for text in sentences_vocab]


    #LDA 모델에 적용하기
    ldamodel = gensim.models.ldamodel.LdaModel(corpus, num_topics=1, id2word = dictionary, passes=5)

    # 결과확인
    LDA_KEYWORD = ldamodel.print_topics(num_topics=1, num_words = 30)
    LDA_KEYWORD = str(LDA_KEYWORD)

    print(re.findall('\\"(.*?)\\"', LDA_KEYWORD))

    lda_main_keyword.append(re.findall('\\"(.*?)\\"', LDA_KEYWORD))
    print(lda_main_keyword)



####### TEST ########



case_keyword = ['동남아_CRT','중국_CRT','일본_CRT','유럽_CRT','대양주_CRT','북미지역_CRT']

#case_keyword = ['동남아']
a = 1
i = 0


# 메인 코드

for i in range(len(case_keyword)):
    print("TEST TEST TEST TEST")
    sentences_vocab_test = []

    for line in codecs.open("C:/Users/VGL_P17041/Documents/%s.txt" %case_keyword[i] , encoding='utf-8'):
        print(line)
        sentences = [word for word in line.split('\n')]
        for sentence in sentences:
            sentences_vocab_test.append(tokenize(sentence))

            # document-term matrix 만들기
        print(get_tags(str(sentences_vocab_test), 100))
        dictionary = corpora.Dictionary(sentences_vocab_test)
        corpus = [dictionary.doc2bow(text) for text in sentences_vocab_test]

            # LDA 모델에 적용하기
        ldamodel = gensim.models.ldamodel.LdaModel(corpus, num_topics=1, id2word=dictionary, passes=5)

            # 결과확인
        LDA_KEYWORD_TEST = ldamodel.print_topics(num_topics=1, num_words=30)
        LDA_KEYWORD_TEST = str(LDA_KEYWORD_TEST)
        LDA_KEYWORD_TEST = re.findall('\\"(.*?)\\"', LDA_KEYWORD_TEST)

        from sklearn.feature_extraction.text import CountVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
        from sklearn.feature_extraction.text import TfidfVectorizer

        동남아_CR = str(lda_main_keyword[0])
        중국_CR = str(lda_main_keyword[1])
        일본_CR = str(lda_main_keyword[2])
        유럽_CR = str(lda_main_keyword[3])
        대양주_CR = str(lda_main_keyword[4])
        북미지역_CR = str(lda_main_keyword[5])

        illegal = [동남아_CR,중국_CR,일본_CR,유럽_CR,대양주_CR,북미지역_CR]
        answer = ['동남아_CR','중국_CR','일본_CR','유럽_CR','대양주_CR','북미지역_CR']
            # print(answer)

        simillarity_dict = {}

        for j in range(len(illegal)):
            train_set = [str(LDA_KEYWORD_TEST), "%s" % illegal[j]]

            # print(train_set)
            tfidf_vectorizer = TfidfVectorizer()
            tfidf_matrix_train = tfidf_vectorizer.fit_transform(train_set)

            # COSINE 유사도 계산
            # cosine_similarity(tfidf_matrix_train[0:1], tfidf_matrix_train)
            simillarity = cosine_similarity(tfidf_matrix_train[0:1], tfidf_matrix_train)
            simillarity_detail = str(simillarity).replace(" ", "").replace("[", '').replace("]", '').replace("1.",
                                                                                                             "")

            simillarity_dict['%s' % answer[j]] = simillarity_detail

        # print(simillarity_dict)
        recommend_case = sorted(simillarity_dict.items(), key=itemgetter(1), reverse=True)[0]
        # print(recommend_case)
        reco_case = recommend_case[0]

        print(i + 1)
        print(reco_case)

        f = open("C:/Users/VGL_P17041/Documents/customer_review_2.txt", 'a')
        customer_review_2 = "%d, %s\n" % (i + 1, reco_case)
        f.write(customer_review_2)
