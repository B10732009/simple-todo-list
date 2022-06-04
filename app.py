from flask import Flask
from flask import render_template, request, url_for, redirect
from datetime import datetime
import database
import uuid

# 建立Flask物件
app = Flask(__name__)

# 建立Database物件
db = database.Database('database')

# 在資料庫中建立USER資料表
db.execute(
    """
        CREATE TABLE USER (
        EMAIL VARCHAR(100) PRIMARY KEY,
        USERNAME VARCHAR(100),
        PASSWORD VARCHAR(100));
    """
)

# 在資料庫中建立NOTE資料表
db.execute(
    """
        CREATE TABLE NOTE (
        UUID VARCHAR(100) PRIMARY KEY,
        USER_EMAIL VARCHAR(100),
        CONTENT VARCHAR(300),
        DATE DATETIME,
        DONE INT);
    """
)

# 建立一字典, 儲存目前登入帳號的資訊, 若為空字典則表示尚未登入
loginUser = {}


### route函式 ###
# 首頁
@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template("home.html", loginUser=loginUser)


# 註冊
@app.route("/signup", methods=['GET', 'POST'])
def signup():
    # 如果是由按下'sign up'按鈕來到這個route
    if request.method == 'POST':
        # 取得request中的資料
        form = dict(request.form)

        # 確認form中'email', 'username', 'password'3項資料都存在
        if form.get('email') and form.get('username') and form.get('password'):
            # 在USER資料表中新增此帳號
            db.execute(
                '''
                    INSERT INTO USER ('EMAIL', 'USERNAME', 'PASSWORD')
                    VALUES ('{}', '{}', '{}');
                '''.format(form['email'], form['username'], form['password'])
            )

            # 更新loginUser資料
            loginUser['email'] = form['email']
            loginUser['username'] = form['username']
            loginUser['password'] = form['password']

            # 註冊成功, 回到首頁
            return redirect(url_for('home'))

    # 顯示註冊頁面
    return render_template("signup.html", loginUser=loginUser)


# 登入
@app.route("/login", methods=['GET', 'POST'])
def login():
    # 如果是由按下'login'按鈕來到這個route
    if request.method == 'POST':
        # 取得request中的資料
        form = dict(request.form)

        # 從USER資料表中尋找符合的帳號
        db.execute(
            '''
                SELECT * FROM USER
                WHERE EMAIL='{}' AND PASSWORD='{}'
            '''.format(form['email'], form['password'])
        )

        # 讀取符合的帳號資料
        data = db.fetch()
        # 確認符合的帳號資料是否為空
        if data:
            # 將該帳號資料存入loginUser變數(字典模式)
            loginUser['email'], loginUser['username'], loginUser['password'] = data[0]

            #登入成功, 回到首頁
            return redirect(url_for('home'))

    # 顯示登入頁面
    return render_template("login.html", loginUser=loginUser)

# 登出


@app.route("/logout", methods=['GET', 'POST'])
def logout():
    # 將loginUser變數資料清空
    loginUser.clear()

    #登出成功, 回到首頁
    return redirect(url_for('home'))

# 個人帳號資料


@app.route("/personalinfo", methods=['GET', 'POST'])
def personalinfo():
    # 確認是否已登入
    if not loginUser:

        #若否, 回到登入頁面
        return redirect(url_for('login'))

    # 如果是由按下'save'按鈕來到這個route
    if request.method == 'POST':
        # 取得request中的資料
        form = dict(request.form)

        # 確認form中'username', 'password'2項資料都存在
        if form.get('username') and form.get('password'):
            # 更新USER資料表中的資料
            db.execute(
                '''
                    UPDATE USER
                    SET USERNAME='{}', PASSWORD='{}'
                    WHERE EMAIL='{}';
                '''.format(form['username'], form['password'], loginUser['email'])
            )

            # 更新loginUser中的資料
            loginUser['username'] = form['username']
            loginUser['password'] = form['password']

    # 顯示個人帳號資料頁面
    return render_template("personalinfo.html", loginUser=loginUser)


# 筆記
@app.route("/note", methods=['GET', 'POST'])
def note():
    # 確認是否已登入
    if not loginUser:
        #若否, 回到登入頁面
        return redirect(url_for('login'))

    # 如果是由按下按鈕來到這個route
    if request.method == 'POST':
        # 取得request中的資料
        form = dict(request.form)

        # 如果form中有'content'項(按下submit按鈕)
        if form.get('content'):
            # 新增筆記
            db.execute(
                '''
                    INSERT INTO NOTE ('UUID', 'USER_EMAIL', 'CONTENT', 'DATE', 'DONE')
                    VALUES ('{}', '{}', '{}', '{}', {});
                '''.format(str(uuid.uuid4()), loginUser['email'],
                           form['content'], datetime.now().strftime("%Y/%m/%d %H:%M"), 0)
            )
        # 如果form中有'delete_uuid'項(按下delete按鈕)
        elif form.get('delete_uuid'):
            # 刪除筆記
            db.execute(
                '''
                    DELETE FROM NOTE
                    WHERE UUID='{}';
                '''.format(form['delete_uuid'])
            )
        # 如果form中有'done'項(按下status欄按鈕)
        elif form.get('done') and form.get('done_uuid'):
            # 更新DONE狀態
            db.execute(
                '''
                    UPDATE NOTE
                    SET DONE={}
                    WHERE UUID='{}';
                '''.format((int(form['done'])+1) % 2, form['done_uuid'])
            )

    # 檢索該帳號所有筆記
    db.execute(
        '''
            SELECT * FROM NOTE
            WHERE USER_EMAIL='{}';
        '''.format(loginUser['email'])
    )

    # 取出筆記資料
    data = db.fetch()

    # 排序筆記
    data.sort(key=lambda d: str((int(d[4])+1) % 2)+str(d[3]), reverse=True)

    # 顯示筆記頁面
    return render_template("note.html", loginUser=loginUser, notes=data)


# 執行app物件
if __name__ == '__main__':
    app.run(debug=True)
