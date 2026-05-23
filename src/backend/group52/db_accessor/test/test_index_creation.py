import group52.db_accessor.group52 as g52
import group52.db_accessor.db_connector as dbc


conn = dbc.DBConnection(dbc.Databases.PROD)
accessor = g52.ReportAccessor(conn)

print(accessor.show_indexs())
