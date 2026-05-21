

import pymysql, pymysql.cursors
# 1. DB 연결: DBOpen()을 호출하여 데이터베이스 서버에 접속합니다.
# 2. SQL 실행:
#    - INSERT, UPDATE, DELETE: RunSQL()을 사용하여 데이터를 변경하고 트랜잭션(Commit/Rollback)을 처리합니다.
#    - SELECT: OpenSQL()을 사용하여 데이터를 조회하고 클래스 내부 변수(self.datas)에 저장합니다.
# 3. 데이터 활용 (SELECT인 경우):
#    - getTotal(), getData(), getAll()을 사용하여 저장된 조회 결과를 필요에 맞게 추출합니다.
# 4. DB 닫기 :
#    - 조회 완료 후 CloseSQL()로 커서를 닫습니다.
#    - 모든 작업 완료 후 DBClose()로 데이터베이스 연결을 완전히 종료합니다.

class DBManager :
    def __init__(self):
       # [워크플로우 0단계: 초기화] DB 연결 객체와 커서 객체를 담을 변수를 준비합니다.
        self.con = None
        self.cursor = None
       # [워크플로우 1단계: DB 연결] 접속 정보를 받아 MySQL 데이터베이스와 연결을 시도합니다.
    def DBOpen(self, host, id, pw, dbname) :
        try :
            self.con = pymysql.connect(
                host=host,
                database=dbname,
                user=id,
                password=pw,
                charset="utf8",
                cursorclass=pymysql.cursors.DictCursor # 쿼리 결과를 딕셔너리 형태로 받기 위한 설정
            )
            print("DB에 연결되었습니다")
            return True # 연결 성공 시 True 반환
        except Exception as e :
            print(e)
            return False # 연결 실패 시 예외 메시지 출력 후 False 반환
       
    def DBClose(self):
        # [워크플로우 마지막 단계: DB 연결 해제] 모든 작업이 끝난 후 DB와의 연결을 끊어 자원을 반환합니다.(자원을 반환한다는게 뭔 소리야?)
        try :
            self.con.close()
            return True
        except Exception as e :
            print(e)
            return False

    def RunSQL(self, sql, datas) :
        # [워크플로우 2단계 - 데이터 변경 쿼리] INSERT, UPDATE, DELETE 등 데이터 변경 작업을 수행합니다.
        print(f"SQL : \n{sql}")
        if datas : # 바인딩할 데이터가 있는 경우
            try :
                self.cursor = self.con.cursor() # 쿼리를 실행할 커서 생성
                count = self.cursor.execute(sql, datas) # 쿼리 실행 후 영향을 받은 행(row)의 개수 반환
                if count < 1 :
                    # 영향을 받은 행이 없다면(실패/조건 불일치) 작업을 취소(Rollback)하고 커서를 닫습니다.
                    print("데이터를 변경하지 못했습니다")
                    self.con.rollback()
                    self.cursor.close()
                    return False
                else :
                    # 성공적으로 변경되었다면 DB에 반영(Commit)합니다.
                    print("데이터를 변경했습니다")
                    self.con.commit()
                    # INSERT 쿼리의 경우 새로 생성된 레코드의 Primary Key 값을 가져옵니다.
                    new_pk = self.cursor.lastrowid
                    self.cursor.close() # 작업 완료 후 커서 종료
                    # 새 PK가 없다면(UPDATE/DELETE 등) 0과 변경된 행 개수를 반환하고, 있다면 새 PK와 행 개수를 반환합니다.
                    if new_pk == 0 :
                        return 0, count
                    else :
                        return new_pk, count
            except Exception as e :
                print(e)
                return False
        else :
            # 쿼리에 필요한 데이터가 전달되지 않았을 경우 처리
            print("데이터 변경사항이 누락되었습니다")
            return False

    def OpenSQL(self, sql, datas=None) :
        # [워크플로우 2단계 - 데이터 조회 쿼리] SELECT 쿼리를 실행하여 데이터를 가져옵니다.
        print(f"SQL : \n{sql}")
        try :
            self.cursor = self.con.cursor() # 조회용 커서 생성
            if datas :
                self.cursor.execute(sql, datas) # 조건 파라미터가 있는 SELECT 쿼리 실행
            else :
                self.cursor.execute(sql)  # 파라미터가 없는 단순 SELECT 쿼리 실행
            # 조회된 모든 데이터를 메모리(self.datas)에 리스트(내부는 딕셔너리) 형태로 저장합니다.
            self.datas = self.cursor.fetchall() # [] / [원소들]
            return True
        except Exception as e :
            print(e)
            return False

    def CloseSQL(self) :
        # [워크플로우 정리 단계: 커서 종료] OpenSQL 실행 시 열어두었던 조회용 커서를 닫아 메모리 누수를 방지합니다.
        try :
            self.cursor.close()
            return True
        except Exception as e:
            print(e)
            return False

    def getData(self, index) :
        # [워크플로우 3단계 - 조회 결과 추출 1] OpenSQL로 가져온 전체 데이터 중 특정 인덱스의 행(row) 하나만 가져옵니다.
        if self.datas : 
            if 0 <= index < self.getTotal() : # 요청한 인덱스가 유효한 범위 내에 있는지 검사
                print("올바른 인덱스입니다")
                return self.datas[index]
            else :
                return False
        else :
            return False

    def getTotal(self) :
        # [워크플로우 3단계 - 조회 결과 추출 2] OpenSQL로 가져온 데이터의 총 개수(행의 수)를 반환합니다.
        if self.datas :
            return len(self.datas)
        else :
            return False

    def getAll(self) :
        # [워크플로우 3단계 - 조회 결과 추출 3] OpenSQL로 가져온 데이터 전체(리스트)를 반환합니다.
        if self.datas :
            return self.datas
        else :
            return None