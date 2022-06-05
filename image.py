from flask import url_for


# 給予圖片的URL
def image(filename):
    return url_for('static', filename=filename)


#給予一字典, 儲存header所有icon的URL
def iconImage():
    icon = {
        'home': image('home.png'),
        'personalinfo': image('personalinfo.png'),
        'note': image('note.png'),
        'login': image('login.png'),
        'logout': image('logout.png'),
        'signup': image('signup.png')
    }
    return icon
