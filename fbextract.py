import  fdb,platform,os

db_server        = os.getenv("DB_HOST", 'host')
db_port          = int(os.getenv("DB_PORT", 'port'))
db_path          = os.getenv("DB_PATH", 'db_path')
db_user          = os.getenv("DB_USER", 'user')
db_password      = os.getenv("DB_PASSWORD", 'password')

def get_connection():
    if platform.system() == 'Windows':
        return fdb.connect(
            host=db_server,
            port=db_port,
            database=db_path,
            user=db_user,
            password=db_password,
            fb_library_name="C:/sklad/x64/fbclient.dll",
            charset="utf-8"
        )
    else:
        return fdb.connect(
            host=db_server,
            port=db_port,
            database=db_path,
            user=db_user,
            password=db_password,
            charset="utf-8"
        )

def get_data(sql,params,mode=1):
    con = get_connection()
    cur = con.cursor()
    cur.execute(sql,params)
    result  = ''
    try:
        if mode == 1:
            result = cur.fetchall()
        if mode == 2:
            result = cur.fetchone()
    except Exception as e:
        print(str(e))
    con.close()
    return result
