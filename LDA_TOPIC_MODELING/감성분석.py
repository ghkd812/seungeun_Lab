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


stemming_keyword = ['입니다', '많은', '있는', '같은', '같습니다', '없는', '있도록', '안녕하세요', '다양한', '있었습니다', '그런', '있게',
                    '아니라', '이런', '있습니다', '있어', '있어서', '미', '인해', '아닌', '불편함이', '있다면', '있고', '자세히', '있는데',
                    '지루하지', '젊은', '무사히', '깊은', '있었지만', '있을', '있다는',  '없고', '안전하게', '있으면', '있었는데', '바쁜',
                    '아쉬운', '작은', '희', '있었다', '적절한', '같네요', '같아요', '안되어', '없네요', '없었습니다', '있지만', '꼼꼼히',
                    '정확한', '사소한', '어떻게', '이러한', '부탁드립니다', '같다', '똑같은', '힘든', '필요한', '철저한', '다르게', '없어서',
                    '없었다', '있었던', '새로운', '없는지',  '많았습니다', '아니고', '꼼꼼하게', '불편하지', '있었고', '있기를', '없다는',
                    '있', '더운', '많은것을', '그런지', '건강하고', '없다', '아닌가요', '분명히', '짧지', '없어', '같고', '진정한', '바쁘게',
                    '지루할', '다르고', '계신', '깊었습니다', '있었으며', '아닐까', '편히', '많으셨습니다', '같아', '편하고', '아무런', '같은데',
                    '박한', '많은것', '없게', '아쉬워서', '완전히', '불편함을', '많았는데', '많아서', '급하게', '있어야', '가까운', '길게', '상당히',
                    '많고', '있다', '무리한', '있나', '확실히', '인한', '그런데도', '궁금합니다', '뻔한', '불편함', '뜨거운', '궁금한', '부족한',
                    '같으', '건강하십시요', '명확하게', '낮은', '멋졌습니다', '멋졌던', '단순히', '단순한', '멋있는', '간절히', '다행히', '아쉽지만',
                    '길어', '넓은', '그렇지', '같다고', '부러운', '부랴', '번거로', '건강하시길', '드문', '많', '같은거', '부족하다', '많았던',
                    '같았는데', '그러면서', '바빠서', '그럼', '많으셨어요', '같다는', '끊임없이', '먼', '새롭게', '힘들고', '힘들었습니다', '있지',
                    '있으니', '짧지만', '힘들었을텐데', '있었음에도', '있었음', '자욱한', '피곤함도', '있었으면', '중요하게', '조용', '힘들',
                    '중요합니다',  '없는데', '없었던것', '없습니다', '없던', '심한', '아니었', '없다고', '있었기에', '아닌가', '야할', '야한다고',
                    '야하는', '안타까웠습니다', '안된다고', '어렵고', '아쉬웠던', '없으며', '있더라고요', '있다고', '있는지', '선하네요', '있는내내',
                    '있는거', '있네요', '있기', '없을', '바쁩니다', '부담스런', '많으시고', '부었는데', '많은지', '복잡하게', '많은데다가',  '많으신',
                    '반했다오', '밤늦게',  '배고프고', '많으시길', '변하지', '변했다', '부끄러운', '반가', '불안한', '부족하였으나', '많았어요', '불편한거',
                    '불편함과', '많았다고', '많아서요', '불편해하는', '붉어지', '비슷하네요', '많아', '빠르고', '많더라구요', '빠른시', '많구나', '뻔한거',
                    '뿐이었다이', '사소한것', '많았었는데', '불편하거나', '불쾌함을', '불쾌한', '부족하지도', '많으셨고', '부족해서요', '부족해지자', '부탁드려요',
                    '부탁드리고', '부탁드리는', '부탁드릴께요', '많으셨구요', '많으며', '분주한', '불가피하게', '불과하답니다', '불안하고', '불안했지만', '불친절하고',
                    '불친절하다', '불쾌하였', '많았지만', '많이는', '못지않게', '바쁘신', '있더군요', '있다면은', '낡은', '있다는게', '있다는거', '있다고해', '있다고하면',
                    '낮으면', '있다가', '낯설어', '있는데요', '있는것처럼', '있는가', '넘치네요', '낡고', '넘치시더라구요', '있던', '나쁨을', '살빠져서', '깊히', '있었던건',
                    '있었던거', '까맣게', '있었답니다', '있었다는', '있었는지', '있었네', '있었긴', '꼬였어요', '있었구요', '나빠', '나쁜', '나열할',
                    '바쁘실텐데도', '있냐', '노란', '무서워하는데', '무책임한', '뭉클했습니다', '많치', '미안하다는', '미안해', '미안해하고', '미어는',
                    '미어에서', '미쳤다', '미치고', '미친', '미친듯이', '바빠', '많지', '많이하고', '바쁘다', '있나요', '무리해서', '무리하지도',
                    '아니거든요', '아니네요', '멀고', '몰지각한', '못마땅했지만', '무능하고', '무뚝뚝하게','있겠으나', '다르지', '없었어요', '없었으나',
                    '없었으며', '없었을', '없었죠', '없었지만', '다르더라구요', '다르다', '없지만', '여려', '역겹고', '연결해', '연히', '열악한',
                    '다름이', '다름이아니라', '없었는데', '없었고요', '없', '없겠죠', '없겠지만', '없겠지요', '당했습니다', '없기', '없네', '당할까봐',
                    '당한것이', '당연히', '담할', '다양하게가야지', '당해', '오래된', '높게', '높고', '인하여', '익숙한', '익숙하지', '어리벙벙한데',
                    '인해서', '우울한', '원망합니다', '원하는것처럼', '원하시는',  '왠만해서', '입니', '입니다다시', '느려서', '높지', '억울함도', '이상한',
                    '놀랬고', '있겠지만', '있었어요', '머나먼', '있겠', '있게끔', '놀라운', '놀라웠다', '입니다이에', '있겠지요', '왠만한', '마르도록',
                    '있긴', '성해서', '소상히', '서운했으나', '서툰', '생생히', '생소한', '생소했지만', '서먹서먹한', '서먹한', '서운함에', '새롭기만',
                    '상관없이', '소소한', '실망한', '싫어하여', '싫었습니다', '싫은', '심하여', '마지못해', '심히', '쎄', '아낌없는', '아니', '심함에도',
                    '소홀함이', '소홀히', '스러웠고', '슬퍼서', '있었으나', '지루하거나', '깊어서', '파랗고', '틀림없다', '특이한', '특별난', '크나큰',
                    '커다란', '같지만', '같은걸', '같아서요', '같았습니다', '편하지만은', '같으며', '추합니다', '추웠는데', '추워하는', '철저히', '계시다면',
                    '계시면서', '고군', '고달픔과', '차가운', '차가', '찜찜한', '계시다는것이', '푸르', '계셔야', '계셨는데', '계시겠죠', '친절하셨지만',
                    '계시다가', '계시다고', '치밀하고', '가벼운', '했습니다', '간단하다', '황당했습니다', '황당하더군요', '환한', '강력하게', '화하던',
                    '화창한', '가득한', '있길', '있겠습니다', '힘듭니다', '힘들지만', '가깝게는', '가녀린', '힘들었던', '가능했습니다', '힘들겠구나',
                    '힘들것', '가득하시고요', '힘든만큼', '가득하신', '힘드실', '화창하여', '화려한', '화려하다는', '헷갈리기', '필요없다고', '피곤했지만',
                    '피곤했을', '피곤함줄', '피곤함이', '피곤함을', '같더라구요', '피곤할텐데', '피곤한', '피곤하지만', '피곤하여', '피곤하실', '피곤하신',
                    '피곤하셨을텐데', '피곤하기만', '피곤하고', '같던', '필요하시다면', '같더라고요', '같다면', '허무한', '강력히주', '강하셨던', '강해져',
                    '같구요', '같는데', '한가한', '있었으니깐', '고마워하는지', '젊어서는', '젊어도', '그럼으로', '전화해서', '그렇게나',
                    '적절하게', '적당히하셔야지', '젊어지고', '적는데', '저렴하다는', '저렴하기', '그렇듯', '그렇다면', '정갈하고', '정갈한', '그러고',
                    '그러네요', '그러던', '좁아', '조용한', '조용하면서도', '조용하고', '조심스러워', '조그마한', '정확한지', '그러지', '정확하게',
                    '있을텐데', '있을지를', '있을까', '있으시면', '있으시길', '있으시기', '있으시고', '있으셨', '있으셔서', '길고', '있으나', '길은',
                    '깊게', '있었을', '깊고', '있음', '그랬지요', '있음에도',  '기대하지', '재미없었는데', '장하면서', '잘난', '잘나셔서', '기대한다',
                    '작디', '자자했습니다', '기대할수', '기대해', '기대해도되', '기대했던', '짜증스러울', '그랬던것', '좋다하여', '고셨습니다', '고야와',
                    '고픈', '중요함을', '중요하지만', '주도하시니', '죄송했습니다', '죄송하고', '죄송하게도', '죄송스럽고', '괜찮다고', '즐건', '짙었던',
                    '진한', '지저분했던', '지루했을', '지루해지기', '지루한', '지루하지도', '지루하였는데', '지루하게', '용합니다', '지겹지', '즐겁과',
                    '좋질', '괜찮았지만', '귀찮은', '귀한', '그래에도', '그랬는대', '그랬는지', '궁금한것', '좋았을', '좋았었지만', '궁금했던', '좋았던건',
                    '좋았던', '이런건', '좋은', '화합시다', '없었고', '비싼', '어떤', '즐거운', '솔직히', '좋게', '없음', '아니면', '좋았습니다', '비슷한', '아닙니까',
                    '좋겠습니다', '좋', '원하는', '좋지', '필요하다고', '중요한', '같아서', '가능한', '빠른', '없으니', '자세한', '좋다고', '정확히',
                    '전화했더니', '충분히', '공정한', '없었다는', '있기에', '있는데도', '없어요', '부탁드린다고', '좋았는데', '답답해서', '굉장히',
                    '좋아하는', '좋고', '좋아서', '조용히', '있었다면', '가능하다고', '필요합니다', '급한', '기대하고', '높은', '그럴', '스러웠습니다',
                    '좋아', '즐겁게', '당연한', '짧게', '뿐이었습니다', '많다고', '없다며', '없도록', '어떠한', '없었네요', '없었던', '없지',
                    '원했습니다', '새로', '비싸게', '이럴',  '이상하게', '있지도', '야하는거', '친절하게', '저렴한', '힘들었고', '가능한지', '친절한',
                    '그러한', '같음', '강력히', '편하게', '같으면', '간단한', '괜찮은', '필요할', '그러니', '궁금하네요', '좋겠네요', '동일하나',
                    '야합니다', '그런건', '궁금해서', '없을거라', '궁금한게',  '야할것', '좋겠고', '더라구요', '그런다고', '아까운', '당당하게', '쓸데없는',
                    '더내', '당연하게', '안되지', '대단한', '좋다는', '없었다고', '있습니까', '만족했던', '야한다는', '있으며', '적정한', '멀쩡히',
                    '빠르게', '저렴하게', '명백한', '있을거라', '전화하여', '재미있고', '성실한', '미치지', '있을지', '유명하다는', '유명한', '소중한',
                    '신중히', '원하는대로', '비싸다고는', '확실한', '특별한', '만족했습니다', '야한다', '같은말을', '많다는', '스럽습니다', '맛있게',
                    '정당한', '있어요', '있었거든요', '스럽네요', '많으니', '전화할', '많습니다', '좋았다', '이렇다는', '있는건', '기대하며', '기대했는데',
                    '가능한데도', '없길래', '있냐고', '아니지', '없는거', '있는것도', '안되는데', '아니었던', '어렵다는', '짧은', '급해', '친절하고',
                    '있거나', '그런줄', '아쉬워', '아찔한', '아름다운', '즐거워', '그렇고', '그렇듯이', '가능하다', '엄청나게', '친절하셔서', '있기는',
                    '가능하고', '아니어서', '중요하다고', '높으신', '아니냐고', '다름', '좋을듯', '아니냐', '아깝습니다', '없더라구요', '좋았을텐데',
                    '아니나', '아니겠지', '없다는거', '좋을', '아니구', '다르다고', '그러', '아깝고', '간단히', '아니라서', '아니라면', '아니라는',
                    '안되니', '고마운', '아니더라도', '좋으련만', '있는게', '고', '있는듯', '같게', '무리는', '같기는', '계셨기에', '강하게', '같은데서',
                    '같고요', '같나요', '무사해야하는데', '같',  '같더라도', '같다구', '같으셨어요', '같지도', '같으니', '같은것', '같이건', '같았어요',
                    '건장한', '검은', '같았고', '같은것은', '같아선', '같은데도', '같습니까', '계셨고', '같지', '같은데를', '같더군요',  '같은데요',
                    '아니었습니다', '아까한', '어떡해', '아니게', '어두워', '얇은', '아니기에', '얇아서', '아니길', '아니다', '아니더군요', '얇게',
                    '약했는데', '아니기', '어떤지는', '아까워서', '어떨지는', '아니였으면', '아까', '어떻건', '야했습니다', '아니더라구요', '아니라고까지',
                    '가깝습니다', '가능하겠습니까', '가능하나', '가능하다고하여', '가능하다면', '무안할', '가능하죠', '가능함으로', '가능했으리라',
                    '가득하고', '가볍게', '간단하게', '간략하게', '가능한지를', '가깝고', '아니셔서', '야할지', '아니었다', '야한다며', '아니었다는',
                    '계셨습니다', '아니었으면', '야하는건', '알차고', '아니었을텐데요', '야했고', '계셨어요', '계시는거냐', '다를까', '다름아니',
                    '멀건', '다양하여', '다양했지만', '다행히도', '단정하지', '달랐고', '멀', '달랐었는데', '담하신다는', '머냐는', '당당하십니다',
                    '당당한', '당당한신', '당당히', '다른지요', '다른데', '다르면', '다르다면', '높네', '높다', '멋있다', '높아서', '높았다고', '멋있게',
                    '높았습니다', '멀쩡했을거라', '높으면', '느림', '맛있는', '멀쩡하게', '능숙하고', '능숙한', '능통한', '멀지만', '멀었구나', '다급하게',
                    '다르', '다르다며', '멀다하고', '멀까', '느슨하게', '당연하겠죠', '당연하지', '드물다', '들뜬', '따뜻한', '딱딱하게', '많으셔서',
                    '떳떳하게', '만족하겠습니다', '만족하여', '만족하였지만', '만족하지', '만족했습니다만', '많길래', '많네요', '많다는거', '많더군요',
                    '많던데', '많았고', '많았었는데요', '많았으나', '많으면', '많았음', '많긴', '넓은데서', '드러', '두꺼운', '당연한게', '당하는줄',
                    '당하지', '당할', '많지는', '대단하시다', '많은에도', '많으십니다', '대수롭지', '더구', '더리', '많으셨는데', '더하면', '더한',
                    '동일하게', '동일하지', '동일한', '대단히', '넓으신', '넓게', '넉넉해서', '귀중하고', '그래', '그래고', '그랬고', '그랬냐는',
                    '그랬다는', '그랬습니다', '그랬을까', '궁금해하는', '그랬지만', '그러기로', '그러냐고', '그러는데', '그러더니', '그러려니', '그러하지',
                    '그러하지도', '그러했는지는', '그런거', '그런것', '그러게요', '그런다고요', '궁금함에', '궁금하였음', '무더워지기', '계시는데',
                    '계시더군요', '무거운', '계신지', '계실텐데', '고마웠습니다', '고만하면', '고맙다', '궁금한거', '고파', '괜찮냐고', '괜찮아졌지만',
                    '괜찮았고', '괜찮은지', '굳어', '궁금하면', '궁금하여', '공정하지', '계셨지만', '그런데요', '그럴리', '껌껌해서', '꼬였다며', '꼼꼼한',
                    '명백히', '낮게', '낮음', '멋지게', '너무하지', '넉넉한', '멋있더라', '나열하기도', '그럴꺼면', '깔끔하게', '기대했는데요', '그럴수',
                    '그럴수도', '그럼에도', '그렇게도', '그렇네요', '그렇다는데', '그렇지는', '그만하고', '길지', '그만한', '급한지', '급했습니다',
                    '급히', '급히가서', '기대하겠습니다', '기대하기는', '기대하는데', '기대합니다', '급격히', '원하는데', '좋을까요', '좋을것',
                    '좋으리라', '좋으려고', '좋았지만', '좋았지', '좋았었고', '좋았어요', '좋았어서', '좋았습니다만', '좋았던게', '좋았던것은',
                    '좋았다고', '좋았기', '좋았겠지만', '좋았겠다라는', '좋아했습니다', '좋아했더니', '좋아해서', '좋아할리', '진정하고', '진실한',
                    '직했습니다', '직한', '즐겁지', '즐겁고', '즐거웠습니다', '즐거워진다', '즐거워서', '즐거울려면', '중요하지', '주도하여', '좋아하여',
                    '좋아하기', '좋아하고', '전화했는데', '전화했고', '전화해서는', '전화해도', '전화할꺼라고', '전화한다며', '전화한다고', '전화한',
                    '전화하면서', '전화하면', '전화하니', '전화하는', '전화하고', '적당히', '저렇든', '전화했는지', '좋아하게', '좋더라', '좋더군요',
                    '좋다면', '좋다고는', '좋다가', '좋고요', '좋게도', '좀', '조심스럽', '조그맣게', '조그마하게', '정확하지', '정통한', '정직하게',
                    '정중한', '조용합니다', '확실하다는', '화했', '행복한', '한적한', '하얗게', '필요해서', '필요해', '필요함', '필요할듯', '필요할것',
                    '필요한지는', '필요한데', '필요한것', '훌륭합니다', '힘들지', '힘들었다고', '필요하지', '힘드시겠지만', '힘드셨을', '흰', '희한한',
                    '흔한게', '휼륭한', '훌륭히', '훌륭했습니다', '힘드시면', '필요하구요', '친절함', '친절하더라도', '충분했었습니다', '충분한',
                    '충분하지', '충분하게', '추히', '촉박하여', '철저하지는', '착한', '착하게', '차분히', '짭짤했을', '짧아서', '친절해서', '친절했던',
                    '친절했었어도', '친절히', '필요없고', '피곤하시더라도', '피곤하겠지만', '포근하고', '편해지시더군요', '편할텐데', '편한지', '편한',
                    '편하고자', '필요하겠습니다', '편안한', '편리하게', '특정한', '특별히', '특별하게', '탁한다고', '탁월한', '칠하는것', '편리함을',
                    '재미있게', '작아요', '용하리라', '용하는', '올바른', '예쁘게', '예민했었나보다', '영원히', '연결하여', '없지는', '없죠', '없을텐데',
                    '없을지', '없을시는', '없을수있다느니', '없을수도', '없을꺼', '없으신','없으시데요', '원하고', '원하는데로', '유익한', '유익하고',
                    '유익하게', '유용한', '유연함의', '유사한', '유리하지', '유리하다', '유능한', '위험하고', '위대한', '웬만하면', '원활하지', '원했기',
                    '원해', '원한다면', '원한다며', '원하지', '원하신다면', '신나게', '없으셨다', '없으니깐', '없으나', '없냐', '없나요', '없나', '없길',
                    '없구', '없고요', '없겠어요', '없겠다는', '없겠네요', '없거나', '엄청날', '없냐고', '없는건', '없는게', '없는데다', '없었음에도',
                    '없었을듯', '없었을까요', '없었을것', '없었으니', '없었던건', '없었기에', '없었기', '없어서요', '유익할지', '없어도', '없던지',
                    '없던데', '없더군', '없다면서', '없다는게', '없다는건', '없다고하며', '없는지도', '없는듯', '없습니다만', '유익했고', '유일한',
                    '유쾌하고', '있었다고', '있었는지요', '있었는데요', '있었네요', '있었나요', '있었겠죠', '있어야죠', '있어도', '있어던', '있습니다만',
                    '있든지', '있든요', '있던데', '있더라도', '있더라구요', '있답니다', '있다하여', '있다하니', '있다지만', '있었어', '있으면서',
                    '있으므로', '있으시겠지만', '작아서', '작게', '자유롭게', '자욱해서', '자세하게', '자비로', '자리라며', '자그만', '있죠', '있다며',
                    '있자니', '있을수있는가', '있을수', '있을만큼', '있을까요', '있을것이다', '있을것으로', '있을거라고', '있은', '있으시다면',
                    '있을지언정', '있다라', '있다고요', '이쁘고', '이렇든', '이렇다', '이렇게만', '이럴진대', '이럴꺼라는', '이런거', '이랬습니다',
                    '의해', '의한', '의하면', '유쾌한', '입나다', '있다고는', '있는지는', '있는데로', '있는대로', '있는것인지요', '있는것이라',
                    '있는것을', '있는건데', '있느냐', '있네여', '있길래', '있기조차도', '있군요', '있구나', '있겠지하고', '있겠습니까', '입을것이라는',
                    '입니다지난', '입니다만', '있나라고', '신나' ,'스러웠어요', '스러워하고', '스러워서', '스러','선량한','아쉬웠는데', '아쉬웠다', '아쉬웠다면']



# 형용사분리 + 불용어 처리 함수
def tokenize(doc):
    sentences_tag = []
    post_tagger = Twitter()
    morph = post_tagger.pos(doc)
    sentences_tag.append(morph)
    print("1. sentences_tag : ", sentences_tag)

    adj_list = []
    for sentence in sentences_tag:
        for word, tag in sentence:
            if tag in ['Adjective']:
                adj_list.append(word)
                adj_list = [''.join(t) for t in adj_list if t not in stemming_keyword]
    return adj_list


# 텍스트에서 형용사 분리하여 빈도 계산
def get_tags(text, ntags):
    adjs = tokenize(text)
    count = Counter(adjs)
    return_list = []
    for n, c in count.most_common(ntags):
        temp = {'tag': n, 'count': c}
        return_list.append(temp)
    return return_list

lda_main_keyword = []

case_keyword = ['긍정','부정']

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
    LDA_KEYWORD = ldamodel.print_topics(num_topics=1, num_words = 1000)
    LDA_KEYWORD = str(LDA_KEYWORD)

    print(re.findall('\\"(.*?)\\"', LDA_KEYWORD))

    lda_main_keyword.append(re.findall('\\"(.*?)\\"', LDA_KEYWORD))
    print(lda_main_keyword)



####### TEST ########



case_keyword = ['북미','동남아']

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

        북미 = str(lda_main_keyword[0])
        동남아 = str(lda_main_keyword[1])


        illegal = [북미, 동남아]
        answer = ['긍정','부정']
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

        f = open("C:/Users/VGL_P17041/Documents/북미_동남아.txt", 'a')
        북미_동남아 = "%d, %s\n" % (i + 1, reco_case)
        f.write(북미_동남아)