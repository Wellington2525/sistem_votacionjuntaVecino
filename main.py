from flask import Flask, render_template, request, redirect, url_for,session,flash,g
from flask_session import Session
# from flask_conndb import conn
# import conndb.cursors
import re
from flask import jsonify,json
#from flask_table import Table, Col, LinkCol
import bcrypt 
import jwt
from werkzeug.security import generate_password_hash, check_password_hash 
from werkzeug.utils import secure_filename 
import pyfiglet
import secrets
import csv
# from flask_login import LoginManager, login_user, logout_user, login_required,UserMixin,current_user
# from wtforms.validators import InputRequired, Length, ValidationError
# import psycopg2
# from psycopg2 import sql
import os
import urllib.request
# import sudo
from flask_mysqldb import MySQL
from flask_login import LoginManager, login_user, logout_user, login_required,UserMixin,current_user
from wtforms.validators import InputRequired, Length, ValidationError

import pymysql


app =Flask(__name__)

db_host = 'localhost'
db_user = 'root'
db_password = ''
db_name = 'votaciones_db'

def conectar_db():
    return pymysql.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        database=db_name,
        cursorclass=pymysql.cursors.DictCursor
        
    )



app.config['SECRET_KEY'] = 'akdsald4654654'
#login_manager = LoginManager(app)
result = pyfiglet.figlet_format("Control Votaciones", font="banner3-D")
print(result)

dir =app.config['UPLOAD_FOLDER'] = '/static/uploads'
print("dir",dir)
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

# app.config['MYSQL_HOST'] = 'localhost'
# app.config['MYSQL_USER'] = 'root'
# app.config['MYSQL_PASSWORD'] = ''
# app.config['MYSQL_DB'] = 'votaciones_db'
# app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
# mysql = MySQL(app)

# try:
#     cur = mysql.connection.cursor()
#     print("Connected to MySQL database!")
# except Exception as e:
#     print("Failed to connect to MySQL database:", e)  




# @app.route('/all')
# def index():
#     global mysql  # Assuming you want to access mysql globally (not recommended)
#     if 'mysql' not in g:
#         app.config['MYSQL_HOST'] = 'localhost'
#         app.config['MYSQL_USER'] = 'root'
#         app.config['MYSQL_PASSWORD'] = ''  # Not recommended for production
#         app.config['MYSQL_DB'] = 'votaciones_db'
#         app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
#         mysql = MySQL(app)
#         g.mysql = mysql  # Store in application context (optional)

#     # Use the 'mysql' object to interact with the database
#     # ...

#     return 'Database connection established!'  # 

            


@app.route("/home",methods=['GET'])
def layout():
    msg=''
    try:
                
        if 'loggedin' in session:
            num=session["num"]
            #std=session['std']
            conexion = conectar_db()
            cur = conexion.cursor()
            
            query="SELECT id,nombre,cedula,email,imagen_path FROM candidatos"
            cur.execute(query)
            data = cur.fetchall()
            ruta_uploads = 'uploads' 
            if data is not None:
               print("NULL")
               
            else:
                for row in data:
                    
                    nombre=row['nombre']
                    cedula =row['cedula']
                    email = row['email']
                    imagen=row['imagen_path']
                print(row)
    #me quede con la ruta de imagen
            return render_template('home.html', data=data,num=num)
        
        else:
            flash('Acceso no autorizado', category='danger')
            return redirect(url_for('acceso_ced'))

 
    except Exception as e:
        print(type(e))  # Agrega esta línea para imprimir el tipo de error
        return jsonify({'error': str(e)})
        flash('Error conexion de la base de datos', category='danger')
        return render_template('acceso.html', error=e)
        #return render_template('home.html', error=e)
      #print("errr" + error)
    
    
    


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/subir_upload', methods=['POST'])
def upload():
    msg=""
    try:
        #msg=""
        #if request.method == 'Post' and 'nombre' in request.form["nombre"] and 'direccion' in request.form["direccion"] and 'file' in request.form["file"] :
        if 'file' not in request.files:
         return redirect(request.url)
        nombre = request.form['nombre']
        cedula = request.form['cedula']
        email = request.form['email']
        
        

        file = request.files['file']

        if file.filename == '':
            return redirect(request.url)

        if file and allowed_file(file.filename):
            
            filename = secure_filename(file.filename)
            
            filepath = os.path.join('static/uploads', filename)
            print(filepath)
            try:
                #os.makedirs(filepath, exist_ok=True)
                #archivo = filename.split("uploads")[-1].lower() !="jpg"
                nombre_archivo = os.path.basename(filepath)
                print("archivo",nombre_archivo)
                conexion = conectar_db()
                cur = conexion.cursor()
                query="INSERT INTO candidatos (nombre,cedula,email,imagen_path) VALUES (%s,%s,%s,%s)"
                value=(nombre, cedula, email, filepath)
                cur.execute(query,value)
                cur.connection.commit()
                
                file.save(filepath)
        
                return redirect(url_for('layout'))
                #return render_template('home.html',msg=msg) 
            

            except Exception as save_error:
                
                print("error", save_error)

        else:
            
            flash('Error la foto no es formato jpg, png')
            return render_template('upload_imagen.html',msg=msg)
    except Exception as e:
        flash('Error conexion de la base de datos', category='danger')
        return render_template('acceso.html', error=e)
        print("errr" + error)
    
    
    
    #return render_template("upload_imagen.html",msg=msg)
    
@app.route("/votos/<int:id>", methods=["Post"])
def votos(id):
   msg=""
   try:

            #candidatos_id = request.form['candidatos_id']


            try:
                if 'loggedin' in session:
                    
                    print("session", session['num'])
                    num = session['num']

                    conexion = conectar_db()
                    cur = conexion.cursor()
                    query="INSERT INTO votos (candidatos_id, voto) VALUES (%s,%s)"
                    query2="Update acceso set std='Inactivo' where num=%s"
                    ced=(num,)
                    value=(id, 1)
                    cur.execute(query,value)
                    cur.execute(query2,ced)
                    cur.connection.commit()
                    


                    return redirect(url_for('logout'))
                    #return render_template('home.html',msg=msg) 
                else:
                    return "<h3>debe iniciar la sesion para poder entrar a la website</h3>", 404
                        
            

            except Exception as save_error:
                print("error", save_error)



   except Exception as e:
        flash('Error conexion de la base de datos', category='danger')
        return render_template('acceso.html', error=e)
        print("errr" + error) 
            
            
            
            
            

@app.route("/form",methods=['GET'])
def form():
    msg=''
    
    
    return render_template('upload_imagen.html',msg=msg)



@app.route("/candidato/<id>", methods=["GET"])
def candidato(id):
    try:
                
        if 'loggedin' in session:
            num=session['num']
            conexion = conectar_db()
            cur = conexion.cursor()
            query="SELECT id,nombre,cedula,email,imagen_path FROM candidatos where id=%s"
            #query2 = "Update acceso set std='Inactivo' where num=num"
            args=[id]
            cur.execute(query,args)
            data = cur.fetchall()
            cur.close()
            # for row in data:
            #     nombre=row['nombre']
            #     cedula =row['cedula']
            #     email = row['email']
            #     imagen=row['imagen_path']
            #print(row)
            
    #me quede con la ruta de imagen
            return render_template('candidato.html', data=data)
        else:
            flash('Acceso no autorizado', category='danger')
            return redirect(url_for('acceso_ced'))

 
    except Exception as e:
        flash('Error conexion de la base de datos', category='danger')
        return render_template('acceso.html', error=e)
        print("errr" + e)
    
@app.route("/estadistica", methods=["GET"])
def estadistica():
    msg=''
    try:
                
        
        conexion = conectar_db()
        cur = conexion.cursor()
        
        query=" SELECT C.nombre AS nombre_candidato,SUM(CAST(V.voto AS SIGNED)) AS total_votos FROM votos V INNER JOIN candidatos C ON V.candidatos_id = C.id GROUP BY C.nombre, V.candidatos_id"
        cur.execute(query)
        resultados_votos = cur.fetchall()
        cur.close()
        ruta_uploads = 'uploads' 
        # for row in data:
        #     nombre=row['nombre']
        #     cedula =row['cedula']
        #     email = row['email']
        #     imagen=row['imagen_path']
        #print(resultados_votos)
         
#me quede con la ruta de imagen
        return render_template('estadistica.html', resultados_votos=resultados_votos)

 
    except Exception as e:
        flash('Error conexion de la base de datos', category='danger')
        return render_template('acceso.html', error=e)
        print("errro" + e)
    

@app.route("/acceso",methods=['GET'])
def acceso():
    msg=''
    
    
    return render_template('acceso.html',msg=msg)


@app.route("/", methods=['GET','Post'])
def acceso_ced():
    msg=''
    try:
            msg = ''
            if request.method == 'POST' and 'cedula' in request.form:
                    accesso = request.form.get('cedula')
                    print("ced", accesso)
                    conexion = conectar_db()
                    cur = conexion.cursor()

                    cur.execute('SELECT num,std FROM acceso WHERE num = %s', (accesso,))
                    account = cur.fetchone()
                    print(account)
                    if account and account['std'] == 'Activo':
                        session['loggedin'] = True
                        # session['std'] = account['std']
                        session['num'] = account['num']
                        session['std'] = account['std']
                        
                        
                        return redirect(url_for('layout'))
                    
                    else:
                        flash('No tiene acceso al sistema', category='danger')
                        return  render_template('acceso.html',msg=msg)
                

                    
            return render_template('acceso.html', msg=msg)
 
    except Exception as e:
        print(type(e))  # Agrega esta línea para imprimir el tipo de error
        return jsonify({'error': str(e)})
    
        
        
        
@app.route("/logout")
def logout():
    session.pop('loggedin', None)
    num= session.pop('num', None)
    #std= session.pop('std', None)
    print("clear", num)
    return redirect(url_for('acceso_ced'))       
        
@app.route('/protected')
@login_required
def protected():
    return "<h3>Página no encontrada</h3>", 404
    


def status_401(error):
    return redirect(url_for('login'))


def status_404(error):
    return "<h3>Página no encontrada</h3>", 404        
    

if __name__ == '__main__':
    app.debug =True
    app.run(host = 'localhost', port =4000)
    