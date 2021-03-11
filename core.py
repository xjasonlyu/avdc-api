import config
from ADC_function import *
# =========website========
from WebCrawler import airav
from WebCrawler import avsox
from WebCrawler import dlsite
from WebCrawler import fanza
from WebCrawler import fc2
from WebCrawler import jav321
from WebCrawler import javbus
from WebCrawler import javdb
from WebCrawler import javlib
from WebCrawler import mgstage
from WebCrawler import xcity


class AVDCError(Exception):
    pass


class NotFound(AVDCError):
    pass


def search(keyword: str) -> dict:
    func_mapping = {
        "airav": airav.main,
        "avsox": avsox.main,
        "fc2": fc2.main,
        "fanza": fanza.main,
        "javdb": javdb.main,
        "javbus": javbus.main,
        "mgstage": mgstage.main,
        "jav321": jav321.main,
        "xcity": xcity.main,
        "javlib": javlib.main,
        "dlsite": dlsite.main,
    }

    # default fetch order list, from the beginning to the end
    sources: list = config.Config().sources().split(',')

    # if the input file name matches certain rules,
    # move some web service to the beginning of the list
    if "avsox" in sources and (re.match(r"^\d{5,}", keyword) or
                               "HEYZO" in keyword or "heyzo" in keyword or "Heyzo" in keyword):
        sources.insert(0, sources.pop(sources.index("avsox")))
    elif "mgstage" in sources and (re.match(r"\d+\D+", keyword) or
                                   "siro" in keyword or "SIRO" in keyword or "Siro" in keyword):
        sources.insert(0, sources.pop(sources.index("mgstage")))
    elif "fc2" in sources and ("fc2" in keyword or "FC2" in keyword):
        sources.insert(0, sources.pop(sources.index("fc2")))
    elif "dlsite" in sources and (
            "RJ" in keyword or "rj" in keyword or "VJ" in keyword or "vj" in keyword):
        sources.insert(0, sources.pop(sources.index("dlsite")))

    metadata: dict = {}
    for source in sources:
        metadata = json.loads(func_mapping[source](keyword))
        # if any service return a valid return, break
        if get_data_state(metadata):
            break

    if not metadata:
        raise NotFound('metadata not found!')

    # ================================================网站规则添加结束================================================

    title = metadata.get('title')
    actor_list = str(metadata.get('actor')).strip(
        "[ ]").replace("'", '').split(',')  # 字符串转列表
    actor_list = [actor.strip() for actor in actor_list]  # 去除空白
    release = metadata.get('release')
    number = metadata.get('number')
    studio = metadata.get('studio')
    source = metadata.get('source')
    runtime = metadata.get('runtime')
    outline = metadata.get('outline')
    label = metadata.get('label')
    series = metadata.get('series')
    year = metadata.get('year')
    cover_small = metadata.get('cover_small', '')
    trailer = metadata.get('trailer', '')
    extrafanart = metadata.get('extrafanart', '')
    imagecut = metadata.get('imagecut')
    tag = str(metadata.get('tag')).strip("[ ]").replace(
        "'", '').replace(" ", '').split(',')  # 字符串转列表 @
    actor = str(actor_list).strip("[ ]").replace("'", '').replace(" ", '')

    if not title or not number:
        raise NotFound('metadata not found!')

    # ====================处理异常字符====================== #\/:*?"<>|
    title = title.replace('\\', '')
    title = title.replace('/', '')
    title = title.replace(':', '')
    title = title.replace('*', '')
    title = title.replace('?', '')
    title = title.replace('"', '')
    title = title.replace('<', '')
    title = title.replace('>', '')
    title = title.replace('|', '')
    release = release.replace('/', '-')
    tmp_arr = cover_small.split(',')
    if len(tmp_arr) > 0:
        cover_small = tmp_arr[0].strip('\"').strip('\'')
    # ====================处理异常字符 END================== #\/:*?"<>|

    # ===  替换Studio片假名
    # studio = studio.replace('アイエナジー', 'Energy')
    # studio = studio.replace('アイデアポケット', 'Idea Pocket')
    # studio = studio.replace('アキノリ', 'AKNR')
    # studio = studio.replace('アタッカーズ', 'Attackers')
    # studio = re.sub('アパッチ.*', 'Apache', studio)
    # studio = studio.replace('アマチュアインディーズ', 'SOD')
    # studio = studio.replace('アリスJAPAN', 'Alice Japan')
    # studio = studio.replace('オーロラプロジェクト・アネックス', 'Aurora Project Annex')
    # studio = studio.replace('クリスタル映像', 'Crystal 映像')
    # studio = studio.replace('グローリークエスト', 'Glory Quest')
    # studio = studio.replace('ダスッ！', 'DAS！')
    # studio = studio.replace('ディープス', 'DEEP’s')
    # studio = studio.replace('ドグマ', 'Dogma')
    # studio = studio.replace('プレステージ', 'PRESTIGE')
    # studio = studio.replace('ムーディーズ', 'MOODYZ')
    # studio = studio.replace('メディアステーション', '宇宙企画')
    # studio = studio.replace('ワンズファクトリー', 'WANZ FACTORY')
    # studio = studio.replace('エスワン ナンバーワンスタイル', 'S1')
    # studio = studio.replace('エスワンナンバーワンスタイル', 'S1')
    # studio = studio.replace('SODクリエイト', 'SOD')
    # studio = studio.replace('サディスティックヴィレッジ', 'SOD')
    # studio = studio.replace('V＆Rプロダクツ', 'V＆R PRODUCE')
    # studio = studio.replace('V＆RPRODUCE', 'V＆R PRODUCE')
    # studio = studio.replace('レアルワークス', 'Real Works')
    # studio = studio.replace('マックスエー', 'MAX-A')
    # studio = studio.replace('ピーターズMAX', 'PETERS MAX')
    # studio = studio.replace('プレミアム', 'PREMIUM')
    # studio = studio.replace('ナチュラルハイ', 'NATURAL HIGH')
    # studio = studio.replace('マキシング', 'MAXING')
    # studio = studio.replace('エムズビデオグループ', 'M’s Video Group')
    # studio = studio.replace('ミニマム', 'Minimum')
    # studio = studio.replace('ワープエンタテインメント', 'WAAP Entertainment')
    # studio = re.sub('.*/妄想族', '妄想族', studio)
    # studio = studio.replace('/', ' ')
    # ===  替换Studio片假名 END

    # 返回处理后的metadata
    metadata['title'] = title
    metadata['actor'] = actor
    metadata['release'] = release
    metadata['cover_small'] = cover_small
    metadata['tag'] = tag
    metadata['year'] = year
    metadata['actor_list'] = actor_list
    metadata.setdefault('extrafanart', extrafanart)

    return metadata


if __name__ == '__main__':
    print(search('abp-119'))
