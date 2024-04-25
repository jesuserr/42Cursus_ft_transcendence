def urlavatar(ori):
    avatar = str(ori)
    if not avatar.find('static/avatars'):
         avatar = '/' + avatar
    return avatar