# Database Func collection

import psycopg2

class DatabaseClass():
    def __init__(self):
    
        #데이터 연결
        self.db = psycopg2.connect(host = 'localhost',
                                   dbname = 'rndgatev',
                                   user = 'postgres',
                                   password ='rndgatev',
                                   port = 8001
                                   )
        # 명령 처리에 사용하는 함수
        self.cursor = self.db.cursor()
        
        
        # 스키마 생성 (스미카가 없을 경우)
        self.cursor.execute("CREATE SCHEMA IF NOT EXISTS F_RCMS;")
        
        
    #테이블 생성 (테이블이 없을 경우)
    def CreateTable(self,strTable):
        
        self.cursor.execute("""
                        CREATE TABLE IF NOT EXISTS F_RCMS.{strTable} (
                        Time SERIAL PRIMARY KEY,
                        Format VARCHAR(10),
                        Name VARCHAR(50),
                        Path VARCHAR(200)
                        )""".format(strTable=strTable)
                        )
            
    
    def __del__(self):
        self.db.close()
        self.cursor.close()
    
    # SQL 명령을 처리 하는 함수
    def execute(self,query,args={}):
        self.cursor.execute(query,args)
                                            #한번에 한줄만 읽어오고 싶을 때는 fetchone(), 지정된 갯수만큼 읽어오고 싶을 땐 fetchmany()
        row = self.cursor.fetchall()        #한번에 여러줄을 읽어옴, 아무래도 마지막 행을 불러오고 싶은 듯 함 
        return row    
    
    # 트랜잭션에 변화가 있을 때 커밋
    def commit(self):
        self.db.commit()
    
    # 스키마 -> 테이블의 집합 
    #insert Data 
    def insertDB(self,strTable,strFormat,strTime,strName,strPath):
        sql = " INSERT INTO F_RCMS.{strTable}(Time,Format,Name,Path) VALUES ('{strTime}','{strFormat}','{strName}','{strPath}') ;".format(strTable=strTable,strFormat=strFormat,strTime=strTime,strName=strName,strPath=strPath)
        try:
            self.cursor.execute(sql)
            self.db.commit()
            
            print(strName+"is saved suceessfully")
        except Exception as e :
            print(" insert DB err ",e) 
    
    # DB 읽어오기
    def readDB(self,strTable):
        sql = " SELECT * FROM  F_RCMS.{strTable}".format(strTable=strTable)
        try:
            self.cursor.execute(sql)
            result = self.cursor.fetchall()
            
            #전체 데이터 출력
            for row in result:
                print(row)
        except Exception as e :
            result = (" read DB err",e)
        
        return result    
    
    
            
    def deleteDB(self,table,primaryKeyValue):
        sql = "DELETE FROM F_RCMS.{table} WHERE Time = {primaryKeyValue};".format(table=table, primaryKeyValue=primaryKeyValue)
        try :
            self.cursor.execute(sql)
            self.db.commit()
            print("Delete Suceess")
        except Exception as e:
            print( "delete DB err", e)
            
    def close(self):
        self.db.close()
        