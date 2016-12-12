# -*- coding: utf-8 -*-
import MySQLdb
from database_setting import *


def connect():
    """
    initialize a connection to the database and return a db
    """
    try:
        db = MySQLdb.connect(HOST_NAME, USER_NAME, PASSWORD, DATABASE_NAME)
        return db
    except:
        raise RuntimeError("An Exception happened with the Database, make sure you are connected")

def close(db):
    """
    close the connection
    """
    db.close()

def get_on_progress_domains(cursor):
    """
    select all domains from the on progress domains that haven't scrapped yet. it takse a cursor and
    return a list of domains
    """
    try:
        cursor.execute("select url from on_progress_domains where is_scrapped = 0")
        return cursor.fetchall()
    except:
        raise RuntimeError("An Exception happened with the Database, make sure you are connected")

def get_on_progress_pages(cursor):
    """
    select all pages from the on progress pages that haven't scrapped yet. it takse a cursor and
    return a list of pages
    """
    try:
        cursor.execute("select page_url from on_progress_pages where is_scrapped = 0")
        return cursor.fetchall()
    except:
        raise RuntimeError("An Exception happened with the Database, make sure you are connected")

def get_all_domains(cursor):
    """
    select all domains from the on domains table. it takse a cursor and
    return a list of domains
    """
    try:
        cursor.execute("select domain_url, max_pages from domains where working = 'no'")
        return cursor.fetchall()
    except:
        raise RuntimeError("An Exception happened with the Database, make sure you are connected")

def insert_domains_into_onprogress(db, domains):
    """
    it tokes a db and a list of domains and insert them into the on_progress_domains
    table, return nothing
    """
    cursor = db.cursor()
    print 'domain-----------------------------------------------------------------------------'
    print domains[0]
    print 'domain-----------------------------------------------------------------------------'
    sql_string = "INSERT INTO on_progress_domains(url, max_pages) VALUES(%s, %s)"
    try:
        cursor.execute(sql_string, domains[0])
        db.commit()
    except:
        cursor.close()
        raise RuntimeError("An Exception happened with the Database, make sure you are connected")
    cursor.close()

def save_pages_to_onprogress_pages(db, pages, domain):
    """
    save scrapped internal links to the on progress pages table
    """
    cursor = db.cursor()
    #get domain id
    try:
        cursor.execute("SELECT domain_id, max_pages FROM on_progress_domains WHERE url = %(d)s", {'d':domain})
        domain_id = cursor.fetchone()
        if domain_id == None:
            print "foriegn key not found"
            return
    except:
        cursor.close()
        raise RuntimeError("An Exception happened with the Database, make sure you are connected")

    for page in pages:
        #if max pages reached
        if domain_id[1] < 0:
            print "max pages reached zero, Terminating crawler for the domain:", domain, "after waiting pages are done processing"
            return
        max_pages_updated = int(domain_id[1]) - 1
        sql_string1 = "INSERT INTO on_progress_pages(domain_id, page_url) VALUES(%s, %s)"
        sql_string2 = "UPDATE on_progress_domains SET max_pages = %s WHERE domain_id = %s"
        try:

            cursor.execute(sql_string1, (int(domain_id[0]), page))
            cursor.execute(sql_string2, (max_pages_updated, domain_id[0]))
            db.commit()
        except:
            cursor.close()
            raise RuntimeError("An Exception happened with the Database, make sure you are connected")
    cursor.close()

def delete_all_onprogress_domains():
    """
    delete all entries from on_progress_domains table
    """
    db = connect()
    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM on_progress_domains")
        db.commit()
    except:
        cursor.close()
        db.close()
        raise RuntimeError("An Exception happened with the Database, make sure you are connected")
    cursor.close()
    db.close()

def delete_all_onprogress_pages():
    """
    delete all entries from on_progress_pages table
    """
    db = connect()
    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM on_progress_pages")
        db.commit()
    except:
        cursor.close()
        db.close()
        raise RuntimeError("An Exception happened with the Database, make sure you are connected")
    cursor.close()
    db.close()

def delete_all_domain_pages():
    """
    delete all entries from domain_pages table
    """
    db = connect()
    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM domain_pages")
        db.commit()
    except:
        cursor.close()
        db.close()
        raise RuntimeError("An Exception happened with the Database, make sure you are connected")
    cursor.close()
    db.close()


def select_unscrapped_page(domain):
    """
    return pages to be scrapped url from a specified domain
    """
    db = connect()
    cursor = db.cursor()
    pages = None
    sql_statement = """
                    SELECT page_url
                    FROM on_progress_pages INNER JOIN on_progress_domains ON on_progress_pages.domain_id = on_progress_domains.domain_id
                    WHERE on_progress_pages.is_scrapped = 0 AND on_progress_domains.url = %(d)s
                    """
    try:
        cursor.execute(sql_statement, {'d':domain})
        pages = cursor.fetchall()

    except:
        cursor.close()
        db.close()
        raise RuntimeError("An Exception happened with the Database, make sure you are connected")
    cursor.close()
    db.close()
    return pages

def get_domain_of_page(page_url):
    """
    get a domain url for a specified page
    """
    db = connect()
    cursor = db.cursor()
    sql_statement = """
                    SELECT on_progress_domains.url
                    FROM on_progress_pages INNER JOIN on_progress_domains ON on_progress_pages.domain_id = on_progress_domains.domain_id
                    WHERE on_progress_pages.page_url = %(d)s
                    """
    try:
        cursor.execute(sql_statement, {'d':page_url})
        page = cursor.fetchone()
    except:
        cursor.close()
        db.close()
        raise RuntimeError("An Exception happened with the Database, make sure you are connected")
    cursor.close()
    db.close()
    return page

def get_domain_id_by_domainurl(domain_url):
    """
    get a domain id for a specified domain url
    """
    db = connect()
    cursor = db.cursor()
    sql_statement = """
                    SELECT domain_id FROM `domains` WHERE domain_url = %(d)s
                    """
    try:
        cursor.execute(sql_statement, {'d':domain_url})
        page = cursor.fetchone()
    except:
        cursor.close()
        db.close()
        raise RuntimeError("An Exception happened with the Database, make sure you are connected")
    cursor.close()
    db.close()
    return page

def insert_domain_page(page,domain_id):
    """
    insert a record into domain_pages table
    """
    db = connect()
    cursor = db.cursor()
    sql_string = "INSERT INTO domain_pages(domain_id, page_url) VALUES(%s, %s)"
    try:
        cursor.execute(sql_string, (int(domain_id[0]), page))
        db.commit()
    except:
        cursor.close()
        raise RuntimeError("An Exception happened with the Database, make sure you are connected")
    cursor.close()
    db.close()


def check_exists_onProgress_pages(db,link):
    """
    check if the page is already in the waiting list or not
    return true if exists, false otherwise
    """
    cursor = db.cursor()
    sql_query = "SELECT page_id FROM on_progress_pages WHERE page_url= %(ln)s"
    try:
        cursor.execute(sql_query, {'ln':link})
        result = cursor.fetchone()
    except:
        cursor.close()
        raise RuntimeError("An Exception happened with the Database, make sure you are connected")
    cursor.close()
    return result is not None

def get_page_id(page_url):
    """
    get a page id for a specified page url
    """
    db = connect()
    cursor = db.cursor()
    sql_statement = """
                    SELECT page_id FROM `domain_pages` WHERE page_url = %(d)s
                    """
    try:
        cursor.execute(sql_statement, {'d':page_url})
        page_id = cursor.fetchone()
    except:
        cursor.close()
        db.close()
        raise RuntimeError("An Exception happened with the Database, make sure you are connected")
    cursor.close()
    db.close()
    return page_id

def insert_link_into_external_link(link, found_date, anchor, link_type):
    """
    insert a record into external links table
    """
    db = connect()
    cursor = db.cursor()
    print "------------------------------------------------------------------------------"
    print "link:",link
    print "link:",found_date
    #print "link:",str(anchor.encode('utf8'))
    print "link:",link_type
    print "------------------------------------------------------------------------------"
    sql_string = "INSERT INTO external_links(link_url, found_date, link_anchor, link_type) VALUES(%s, %s, %s, %s)"
    try:
        # Enforce UTF-8 for the connection.
        cursor.execute('SET NAMES utf8mb4')
        cursor.execute("SET CHARACTER SET utf8mb4")
        cursor.execute("SET character_set_connection=utf8mb4")
        cursor.execute(sql_string, (link, found_date, anchor, link_type))
        db.commit()
    except:
        cursor.close()
        raise RuntimeError("An Exception happened with the Database, make sure you are connected")
    cursor.close()
    db.close()

def update_table(table_name, url):
    """
    update a record in the given table to make
    is_scrapped = 1
    """
    if table_name == "on_progress_pages":
        sql_query = "UPDATE on_progress_pages SET is_scrapped=1 WHERE page_url = %s"
    elif table_name == "on_progress_domains":
        sql_query = "UPDATE on_progress_domains SET is_scrapped=1 WHERE url = %s"
    else:
        print "unknown ERROR"
        return
    db = connect()
    cursor = db.cursor()
    try:
        cursor.execute(sql_query, (url,))
        db.commit()
    except:
        cursor.close()
        raise RuntimeError("An Exception happened with the Database, make sure you are connected")
    cursor.close()
    db.close()

def update_link_into_external_link(link_id, date):
    sql_query = "UPDATE external_links SET found_date= %s, `link_on_page` = 'yes' WHERE link_id = %s"
    db = connect()
    cursor = db.cursor()
    try:
        cursor.execute(sql_query, (date, link_id))
        db.commit()
    except:
        cursor.close()
        raise RuntimeError("An Exception happened with the Database, make sure you are connected")
    cursor.close()
    db.close()

def update_domain_status_to_down(domain):
    sql_query = "UPDATE domains SET domain_status = 0 WHERE domain_url = %s"
    db = connect()
    cursor = db.cursor()
    try:
        cursor.execute(sql_query, (domain, ))
        db.commit()
    except:
        cursor.close()
        raise RuntimeError("An Exception happened with the Database, make sure you are connected")
    cursor.close()
    db.close()

def save_external_link_state_to_db(link_id, status):
    sql_query = "UPDATE external_links SET link_status = %s WHERE link_id = %s"
    db = connect()
    cursor = db.cursor()
    try:
        cursor.execute(sql_query, (status, link_id))
        db.commit()
    except:
        cursor.close()
        raise RuntimeError("An Exception happened with the Database, make sure you are connected" + str(link_id) + str(status))
    cursor.close()
    db.close()


def external_link_already_exists(external_link):
    """
    takes an external link and returns a boolean
    true if it's already exists in the table external_links, false otherwise
    """
    sql_query = "SELECT link_id, link_anchor FROM external_links WHERE link_url = %(external_link)s"
    db = connect()
    cursor = db.cursor()
    try:
        cursor.execute(sql_query, {"external_link" : external_link})
        tmp = cursor.fetchall()
    except:
        cursor.close()
        raise RuntimeError("An Exception happened with the Database, make sure you are connected")
    cursor.close()
    db.close()
    return tmp

def select_external_link_url_with_no_null_state():
    db = connect()
    cursor = db.cursor()
    sql_statement = """
                    SELECT link_id, link_url FROM external_links
                    """
    try:
        cursor.execute(sql_statement)
        links = cursor.fetchall()
    except:
        cursor.close()
        db.close()
        raise RuntimeError("An Exception happened with the Database, make sure you are connected")
    cursor.close()
    db.close()
    return links

def get_all_assignment_domains_from_assignments_table():
    db = connect()
    cursor = db.cursor()
    sql_statement = """
                    SELECT assignment_domain FROM assignments WHERE 1
                    """
    try:
        cursor.execute(sql_statement)
        links = cursor.fetchall()
    except:
        cursor.close()
        db.close()
        raise RuntimeError("An Exception happened with the Database, make sure you are connected")
    cursor.close()
    db.close()
    return links

def get_assignment_id_by_assignment_domain(assignment_domain):
    db = connect()
    cursor = db.cursor()
    sql_statement = """
                    SELECT assignment_id FROM assignments WHERE assignments.assignment_domain = %(assign_domain)s
                    """
    try:
        cursor.execute(sql_statement, {"assign_domain": assignment_domain})
        assignment_id = cursor.fetchone()
    except:
        cursor.close()
        db.close()
        raise RuntimeError("An Exception happened with the Database, make sure you are connected")
    cursor.close()
    db.close()
    return assignment_id

def check_domainId_assignmentId_already_exists(domain_id, assignment_id):
    db = connect()
    cursor = db.cursor()
    sql_statement = """
                    SELECT * FROM `assignments_to_domains` WHERE domain_id = %(domain_id)s and assignment_id = %(assignment_id)s
                    """
    try:
        cursor.execute(sql_statement, {"domain_id": domain_id, "assignment_id":assignment_id})
        result = cursor.fetchone()
    except:
        cursor.close()
        db.close()
        raise RuntimeError("An Exception happened with the Database, make sure you are connected")
    cursor.close()
    db.close()
    return result != None

def save_domainId_assignmentId(domain_id, assignment_id):
    db = connect()
    cursor = db.cursor()
    sql_statement = """
                    INSERT INTO assignments_to_domains(domain_id, assignment_id) VALUES (%s, %s)
                    """
    try:
        cursor.execute(sql_statement, (domain_id, assignment_id) )
        db.commit()
    except:
        cursor.close()
        db.close()
        raise RuntimeError("An Exception happened with the Database, make sure you are connected")
    cursor.close()
    db.close()

def get_all_domains_id():
    db = connect()
    cursor = db.cursor()
    sql_statement = """
                    SELECT domain_id FROM `domains` WHERE 1
                    """
    try:
        cursor.execute(sql_statement)
        result = cursor.fetchall()
    except:
        cursor.close()
        db.close()
        raise RuntimeError("An Exception happened with the Database, make sure you are connected")
    cursor.close()
    db.close()
    return result

def get_all_assignments_id():
    db = connect()
    cursor = db.cursor()
    sql_statement = """
                    SELECT assignment_id FROM `assignments` WHERE 1
                    """
    try:
        cursor.execute(sql_statement)
        result = cursor.fetchall()
    except:
        cursor.close()
        db.close()
        raise RuntimeError("An Exception happened with the Database, make sure you are connected")
    cursor.close()
    db.close()
    return result

def select_domain_id_from_assignments_to_domains(assignment_id):
    db = connect()
    cursor = db.cursor()
    sql_statement = """
                    SELECT domain_id FROM `assignments_to_domains` WHERE assignment_id = %(assignment_id)s
                    """
    try:
        cursor.execute(sql_statement, {"assignment_id":assignment_id})
        result = cursor.fetchall()
    except:
        cursor.close()
        db.close()
        raise RuntimeError("An Exception happened with the Database, make sure you are connected")
    cursor.close()
    db.close()
    return result

def select_assignment_id_from_assignments_to_domains(domain_id):
    db = connect()
    cursor = db.cursor()
    sql_statement = """
                    SELECT assignment_id FROM `assignments_to_domains` WHERE domain_id = %(domain_id)s
                    """
    try:
        cursor.execute(sql_statement, {"domain_id":domain_id})
        result = cursor.fetchall()
    except:
        cursor.close()
        db.close()
        raise RuntimeError("An Exception happened with the Database, make sure you are connected")
    cursor.close()
    db.close()
    return result

def update_assignments_links_count_db(links_count, assignment_id):
    db = connect()
    cursor = db.cursor()
    sql_statement = """
                    UPDATE assignments SET links_count = %s WHERE assignment_id = %s
                    """
    try:
        cursor.execute(sql_statement, (links_count, assignment_id) )
        db.commit()
    except:
        cursor.close()
        db.close()
        raise RuntimeError("An Exception happened with the Database, make sure you are connected")
    cursor.close()
    db.close()

def update_domains_links_count_db(links_count, domain_id):
    db = connect()
    cursor = db.cursor()
    sql_statement = """
                    UPDATE domains SET assignments_count = %s WHERE domain_id = %s
                    """
    try:
        cursor.execute(sql_statement, (links_count, domain_id) )
        db.commit()
    except:
        cursor.close()
        db.close()
        raise RuntimeError("An Exception happened with the Database, make sure you are connected")
    cursor.close()
    db.close()

def update_domain_ip_address_db(ip_address, domain):
    db = connect()
    cursor = db.cursor()

    sql_statement = """
                    SELECT ip_address FROM domains WHERE domain_url = %(domain)s
                    """
    try:
        cursor.execute(sql_statement, {"domain":domain})
        result = cursor.fetchone()
    except:
        cursor.close()
        db.close()
        raise RuntimeError("An Exception happened with the Database, make sure you are connected")
    if result is None:
        return
    if len(result[0]) > 0:
        return
    sql_statement = """
                    UPDATE domains SET ip_address = %s WHERE domain_url = %s
                    """
    try:
        cursor.execute(sql_statement, (ip_address, domain) )
        db.commit()
    except:
        cursor.close()
        db.close()
        raise RuntimeError("An Exception happened with the Database, make sure you are connected")
    cursor.close()
    db.close()

def update_last_crawled_date_db(now, domain):
    db = connect()
    cursor = db.cursor()
    sql_statement = """
                    UPDATE domains SET last_crawled = %s, working = 'yes' WHERE domain_url = %s
                    """
    try:
        cursor.execute(sql_statement, (now, domain) )
        db.commit()
    except:
        cursor.close()
        db.close()
        raise RuntimeError("An Exception happened with the Database, make sure you are connected")
    cursor.close()
    db.close()

def make_page_source_type_mainPage(page_url):
    db = connect()
    cursor = db.cursor()
    sql_statement = """
                    UPDATE domain_pages SET source_type = 'mainPage' WHERE page_url = %s
                    """
    try:
        cursor.execute(sql_statement, (page_url,) )
        db.commit()
    except:
        cursor.close()
        db.close()
        raise RuntimeError("An Exception happened with the Database, make sure you are connected")
    cursor.close()
    db.close()

def update_outband_links_count_db(num_links, page_id):
    db = connect()
    cursor = db.cursor()
    sql_statement = """
                    UPDATE domain_pages SET outband_links_count = %s WHERE page_id = %s
                    """
    try:
        cursor.execute(sql_statement, (num_links, page_id) )
        db.commit()
    except:
        cursor.close()
        db.close()
        raise RuntimeError("An Exception happened with the Database, make sure you are connected")
    cursor.close()
    db.close()

def select_external_link_didnot_found_today(today_date, page_id):
    db = connect()
    cursor = db.cursor()
    sql_statement = """
                    SELECT external_links.link_id FROM `external_links` INNER JOIN domain_pages_to_external_links
                    ON external_links.link_id = domain_pages_to_external_links.external_link_id
                    WHERE external_links.found_date != %(today_date)s and domain_pages_to_external_links.domain_page_id = %(page_id)s
                    """
    try:
        cursor.execute(sql_statement, {"today_date":today_date, "page_id" : page_id})
        result = cursor.fetchall()
    except:
        cursor.close()
        db.close()
        raise RuntimeError("An Exception happened with the Database, make sure you are connected")
    cursor.close()
    db.close()
    return result

def update_external_link_on_page_db(link_id):
    db = connect()
    cursor = db.cursor()
    sql_statement = """
                    UPDATE external_links SET link_on_page = "No", link_status = "No Link" WHERE link_id = %s
                    """
    try:
        cursor.execute(sql_statement, (link_id, ) )
        db.commit()
    except:
        cursor.close()
        db.close()
        raise RuntimeError("An Exception happened with the Database, make sure you are connected")
    cursor.close()
    db.close()

def make_domain_working_done_db():
    db = connect()
    cursor = db.cursor()
    sql_statement = """
                    UPDATE domains SET working = "done" WHERE working = "yes"
                    """
    try:
        cursor.execute(sql_statement)
        db.commit()
    except:
        cursor.close()
        db.close()
        raise RuntimeError("An Exception happened with the Database, make sure you are connected")
    cursor.close()
    db.close()

def make_domain_working_error_db():
    db = connect()
    cursor = db.cursor()
    sql_statement = """
                    UPDATE domains SET working = "error" WHERE working = "yes"
                    """
    try:
        cursor.execute(sql_statement)
        db.commit()
    except:
        cursor.close()
        db.close()
        raise RuntimeError("An Exception happened with the Database, make sure you are connected")
    cursor.close()
    db.close()

def get_mailing_options():
    db = connect()
    cursor = db.cursor()
    sql_statement = """
                    SELECT `smtp_login_email`, `smtp_server`, `smtp_login_password`, `port` from email_options
                    """
    try:
        cursor.execute(sql_statement)
        result = cursor.fetchone()
    except:
        cursor.close()
        db.close()
        raise RuntimeError("An Exception happened with the Database, make sure you are connected")
    cursor.close()
    db.close()
    return result

def get_mailing_to_list():
    db = connect()
    cursor = db.cursor()
    sql_statement = """
                    SELECT `to_email` FROM email_to
                    """
    try:
        cursor.execute(sql_statement)
        result = cursor.fetchall()
    except:
        cursor.close()
        db.close()
        raise RuntimeError("An Exception happened with the Database, make sure you are connected")
    cursor.close()
    db.close()
    return result

def select_unfinshed_domain_db():
    db = connect()
    cursor = db.cursor()
    sql_statement = """
                    SELECT `domain_id` FROM `domains` WHERE working = "yes"
                    """
    try:
        cursor.execute(sql_statement)
        result = cursor.fetchone()
    except:
        cursor.close()
        db.close()
        raise RuntimeError("An Exception happened with the Database, make sure you are connected")
    cursor.close()
    db.close()
    return result

def insert_domain_pages_to_external_links(external_id, page_id):
    db = connect()
    cursor = db.cursor()
    sql_statement = """
                    INSERT INTO domain_pages_to_external_links(`domain_page_id`, `external_link_id`) VALUES(%s, %s)
                    """
    try:
        cursor.execute(sql_statement, (page_id, external_id))
        db.commit()
    except:
        cursor.close()
        db.close()
        raise RuntimeError("An Exception happened with the Database, make sure you are connected")
    cursor.close()
    db.close()

def select_domain_pages_to_external_links(external_id, page_id):
    db = connect()
    cursor = db.cursor()
    sql_statement = """
                    SELECT `id` FROM `domain_pages_to_external_links` WHERE domain_page_id = %(page_id)s AND external_link_id = %(external_id)s
                    """
    try:
        cursor.execute(sql_statement, {"page_id":page_id, "external_id":external_id})
        result = cursor.fetchone()
    except:
        cursor.close()
        db.close()
        raise RuntimeError("An Exception happened with the Database, make sure you are connected")
    cursor.close()
    db.close()
    return result
