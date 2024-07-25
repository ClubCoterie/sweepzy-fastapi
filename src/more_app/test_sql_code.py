
# self.conn = self.get_sql_conn()
# self.cur = self.conn.cursor()

# def get_sql_conn(self):
#     try:
#         conn = sqlite3.connect('../sweepzy.db')
#         return conn
#     except sqlite3.Error as e:
#         print(e)

# def update_table(self, df, table_name, df_cols):
#     '''Create Table if not exists with min code.'''
#     df.iloc[0:0].to_sql(name=table_name, con=self.conn, if_exists="append", index=False)
#
#     sql_delete = f'''DELETE FROM {table_name} WHERE tourney_id = {self.tourney_id}'''
#
#     sql_insert = f'''INSERT INTO {table_name}({", ".join(df_cols)})
#                       VALUES({"?," * (len(df_cols) - 1)}?)'''
#
#     self.cur.execute(sql_delete)
#     self.conn.commit()
#     for row in df.itertuples(index=False):
#         print(row)
#         self.cur.execute(sql_insert, row)
#     self.conn.commit()