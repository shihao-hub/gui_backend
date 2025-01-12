import mongoengine
from mongoengine import Document, StringField, IntField

_ = mongoengine.connect(db="0", alias="0")


class User(Document):
    objects: mongoengine.queryset.queryset.QuerySet
    meta = {"collection": "t_users", "db_alias": "0"}

    username = StringField(required=True, max_length=50)
    email = StringField(required=True)
    age = IntField()

    def __str__(self):
        return self.username


def main():
    # 创建并保存一个新用户
    user = User(username='testuser', email='user@example.com', age=30)
    if User.objects.filter(username='testuser').first() is None:
        user.save()

    # 查询用户
    found_user = User.objects.filter(username='testuser').first()
    print(found_user.email)  # 输出：user@example.com

    # 更新用户
    found_user.age = 31
    found_user.save()

    # 删除用户
    # found_user.delete()

    # 复合查询
    users = User.objects(age__gte=18)  # 查询年龄大于或等于18岁用户
    print(users)

    # 过滤用户名以某个字符串开头的用户
    filtered_users = User.objects(username__istartswith='test')
    print(filtered_users)


if __name__ == '__main__':
    main()
