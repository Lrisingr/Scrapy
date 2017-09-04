from scrapy.loader import ItemLoader
from scrapy.loader.processors import Compose,MapCompose,Join,TakeFirst

clean_text = Compose(MapCompose(lambda v: v.strip, Join()))
to_int = Compose(TakeFirst(),int)

class TechCrunchArticleLoader(ItemLoader):
    default_input_processor = MapCompose(lambda s:unicode(s,"utf-8"),unicode.strip)
    default_output_processor = Join()

    tags_in = MapCompose(unicode.strip)
    tags_out = Join(separator=u'; ')

    title_in = MapCompose(unicode.strip, unicode.title)
    title_out = Join()

    text_in = MapCompose(unicode.strip)
    text_out = Join()
