from haystack import indexes
from .models import Enterprise


# whoosh搜索的索引文件
class EnterpriseIndex(indexes.SearchIndex, indexes.Indexable):
    # text为索引字段
    # document = True，这代表haystack和搜索引擎将使用此字段的内容作为索引进行检索
    # use_template=True 指定根据表中的那些字段建立索引文件的说明放在一个文件中
    text = indexes.CharField(document=True, use_template=True)
    name = indexes.CharField(model_attr='name')

    # 对Enterprise表进行查询
    def get_model(self):  # 重载get_model方法
        # 返回这个model
        return Enterprise

    # 建立索引的数据
    def index_queryset(self, using=None):
        # 这个方法返回什么内容，最终就会对那些方法建立索引，这里是对所有字段建立索引
        return self.get_model().objects.all()
