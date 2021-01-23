import logging

from qiniu import Auth, put_data
from django.conf import settings

# 七牛云上传图片配置
# 需要填写你的 Access Key 和 Secret Key
access_key = 'Si_jSqAPyMNvhQb5L9dc57HHEfA7ZPswA9Teypik'
secret_key = 'q236R2ZJJQM-4aknL6BHDFo6C9nfkb7wUsGKDnbp'
QINIUYUN_URL = 'http://qn9m29tnk.hn-bkt.clouddn.com/'
# 要上传的空间，填你的bucket名
bucket_name = 'zufang810'


# 传入图片文件
def storage(data):
    """七牛云存储上传文件接口"""
    if not data:
        return None
    try:
        # 构建鉴权对象
        q = Auth(access_key, secret_key)

        # 生成上传 Token，也可以指定过期时间等
        token = q.upload_token(bucket_name)

        # 上传文件
        ret, info = put_data(token, None, data)

    except Exception as e:
        logging.error(e)
        raise e  # 断言

    if info and info.status_code != 200:
        raise Exception("上传文件到七牛失败")

    # 返回七牛中保存的图片名，这个图片名也是访问七牛获取图片的路径
    print(ret["key"])
    return ret["key"]


if __name__ == '__main__':
    # file_name = input("输入上传的文件")
    file_name = r'F:\tupian\suibian.jpg'
    with open(file_name, "rb") as f:
        storage(f.read())
