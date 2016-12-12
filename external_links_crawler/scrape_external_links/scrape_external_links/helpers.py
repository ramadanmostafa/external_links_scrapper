from database_functions import *
import datetime
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

def check_fresh_crawler():
    """
    check if the last crawler was crashed or paused
    returns a bool, false if the last crawler is unfinished, true if it's a fresh crawler
    """
    domain = select_unfinshed_domain_db()
    if domain is None:
        return True
    if len(domain) < 1:
        return True
    return False

def clean_onprogress_tables():
    """
    delete all entries from on progress domains and on progress pages
    """
    delete_all_onprogress_domains()
    delete_all_onprogress_pages()
    #delete_all_domain_pages()
#clean_onprogress_tables()


def init_onprogress_domain():
    """
    init onprogress domain table with the domains to be scrapped and return the domains
    """
    db = connect()
    cursor = db.cursor()
    all_domains = get_all_domains(cursor)
    if all_domains is None:
        return tuple()
    if len(all_domains) < 1:
        return tuple()
    print 'all_domains-----------------------------------------------------------------------------'
    print all_domains
    print 'all_domains-----------------------------------------------------------------------------'
    insert_domains_into_onprogress(db, all_domains)
    cursor.close()
    close(db)
    domains = []
    for d in all_domains:
        domains.append(d[0])
    return domains

def insert_into_onprogress_pages(pages, domain):
    """
    take a list of pages url and a domain to insert them into on progress pages table
    """
    db = connect()
    unique_pages = []
    for link in pages:
        if not check_exists_onProgress_pages(db,link):
            unique_pages.append(link)
        print unique_pages
    save_pages_to_onprogress_pages(db, unique_pages, domain)
    db.close()

def is_pages_to_be_scrapped(domain):
    """
    check if a specified domain has a page at least to be scrapped,
    return the pages otherwise None
    """
    page = select_unscrapped_page(domain)
    if page is None:
        return None
    return page

def get_domain_by_pageUrl(page_url):
    """
    get a domain url for a specified page
    """
    return get_domain_of_page(page_url)

def get_domain_id_by_page_url(page_url):
    domain_url = get_domain_by_pageUrl(page_url)
    domain_id = get_domain_id_by_domainurl(domain_url)
    return domain_id

def save_url_to_domainPages(page_url):
    """
    save the page url to domain pages table
    """
    domain_url = get_domain_of_page(page_url)
    domain_id = get_domain_id_by_domainurl(domain_url)
    page_id_old = get_page_id(page_url)
    if page_id_old is None:
        insert_domain_page(page_url, domain_id)
    page_id = get_page_id(page_url)
    return page_id

def update_waiting_list(internal_links, domain):
    """
    update the waiting list with the scrapped internal links
    """
    db = connect()
    for link in internal_links:
        if not check_exists_onProgress_pages(db, link):
            save_pages_to_onprogress_pages(db, [link], domain)

    db.close()

def get_today_date():
    """
    returns the date of today in format (YYYY-MM-DD)
    """
    now = datetime.datetime.now()
    return str(now.year) + "-" + str(now.month) + "-" + str(now.day)

def save_external_links(external_links, page_id, anchors, link_type):
    """
    add the external links scrapped to the Database
    """
    found_date = get_today_date()
    for key, link in external_links.items():
        #check if it's already exists
        #link_id, link_anchor
        data = external_link_already_exists(link)
        if data != None and len(data) > 0:
            flag = False
            for item in data:
                if item[1] == anchors[key]:
                    flag = True
                    external_id = item[0]
                    break

            if not flag:
                #
                external_id = insert_link_into_external_link(link, found_date, anchors[key], link_type[key])
                if select_domain_pages_to_external_links(external_id, page_id) is None:
                    insert_domain_pages_to_external_links(external_id, page_id)
            else:
                #update last seen
                #
                update_link_into_external_link(external_id, found_date)
                if select_domain_pages_to_external_links(external_id, page_id) is None:
                    insert_domain_pages_to_external_links(external_id, page_id)
        else:
            #insert link into the external link table
            #page_id, link_url, found_date
            #
            external_id = insert_link_into_external_link(link, found_date, anchors[key], link_type[key])
            if select_domain_pages_to_external_links(external_id, page_id) is None:
                insert_domain_pages_to_external_links(external_id, page_id)

def make_page_scrapped(page_url):
    """
    update the page record in the on progress pages table to make
    is_scrapped = 1
    """
    update_table("on_progress_pages", page_url)

def make_domain_scrapped(domain_url):
    """
    update the domain record in the on progress domains table to make
    is_scrapped = 1
    """
    update_table("on_progress_domains", domain_url)

def prepare_to_continue_scrapper():
    """
    get some info from db to continue the scrapper
    """
    db = connect()
    cursor = db.cursor()
    all_domains = get_on_progress_domains(cursor)
    all_pages = get_on_progress_pages(cursor)
    cursor.close()
    close(db)
    if len(all_pages) < 1:
        return all_domains,None, None
    print "iam here -------------------------------------------------------------------------------------"
    print all_pages,type(all_pages)
    print "iam here -------------------------------------------------------------------------------------"
    current_domain = get_domain_of_page(all_pages[0])##############################################
    #all_domains.remove(current_domain)
    all_domains_updated = []
    for d in all_domains:
        if d != current_domain:
            all_domains_updated.append(d)
    return all_domains_updated, all_pages, current_domain

def check_url(url):
    """
    check if the given url is a true url or not
    """
    import re
    pattern = r"^((https?):((//)|(\\\\))+([\w\d:#@%/;$()~_?\+-=\\\.&](#!)?)*)"
    return re.search(pattern, url) != None

def internal_or_external(page_url, domain):
    """
    checks if the page url belongs to that domain or not
    return boolean
    true of internal, false if external
    """
    from urlparse import urlparse
    domain_netloc = urlparse(domain).netloc
    return domain_netloc in page_url

def change_domain_status_to_down(domain):
    update_domain_status_to_down(domain)

def save_external_link_state(link_id, status):
    save_external_link_state_to_db(link_id, status)

def select_external_link_with_no_state():
    select_external_link_url_with_no_null_state()

def get_all_assignment_domains():
    return get_all_assignment_domains_from_assignments_table()

def save_assignment_domain(domain_id, assignment_domain):
    #get assignment_id by assignment_domain
    assignment_id = get_assignment_id_by_assignment_domain(assignment_domain)[0]
    #check if (domain_id, assignment_id) already exists if not,
    #insert into assignments_to_domains (domain_id, assignment_id)
    if not check_domainId_assignmentId_already_exists(domain_id, assignment_id):
        save_domainId_assignmentId(domain_id, assignment_id)

def update_assignments_links_count():
    #get all assignments id
    all_assignments_id = get_all_assignments_id()
    for assignment_id in all_assignments_id:
    #   SELECT domain_id from assignments_to_domains WHERE assignment_id = current
        result = select_domain_id_from_assignments_to_domains(assignment_id[0])
        if result is not None:
            tmp = len(result)
            update_assignments_links_count_db(tmp, assignment_id[0])

def update_domains_assignments_count():
    #get all domains id
    all_domains_id = get_all_domains_id() #list of tuples
    for domain_id in all_domains_id:
    #   SELECT assignment_id from assignments_to_domains WHERE domain_id = current
        result = select_assignment_id_from_assignments_to_domains(domain_id[0])
        if result is not None:
            tmp = len(result)
            update_domains_links_count_db(tmp, domain_id[0])

def update_domain_ip_address(domain):

    if type(domain) is type(tuple()):
        domain = domain[0]
    domain_netloc = domain
    if str(domain).startswith('http'):
        from urlparse import urlparse
        domain_netloc = urlparse(domain).netloc
    import socket
    ip_address = socket.gethostbyname(domain_netloc)
    print ip_address
    print "iam here -------------------------------------------------------------------------------------"
    print domain ,type(domain)
    print "iam here -------------------------------------------------------------------------------------"
    update_domain_ip_address_db(ip_address, domain)

def update_last_crawled_date(domain):
    now = str(datetime.datetime.now())
    update_last_crawled_date_db(now, domain)

def update_source_page(page_url):
    make_page_source_type_mainPage(page_url)

def update_outband_links_count(num_links, page_id):
    update_outband_links_count_db(num_links, page_id)

def update_external_link_on_page(page_id):
    today_date = get_today_date()
    unfound_links_ids = select_external_link_didnot_found_today(today_date, page_id)
    print unfound_links_ids
    if unfound_links_ids == None:
        return
    for link_id in unfound_links_ids:
        update_external_link_on_page_db(link_id[0])

def make_domain_working_done():
    make_domain_working_done_db()

def make_domain_working_error():
    make_domain_working_error_db()

def get_mailing_info():
    data = get_mailing_options()
    smtp_login_email = data[0]
    smtp_server = data[1]
    smtp_login_password = data[2]
    port = data[3]
    print smtp_login_email, smtp_server, smtp_login_password, port
    data = get_mailing_to_list()
    mailing_to_list = []
    for item in data:
        mailing_to_list.append(item[0])
    print mailing_to_list
    return smtp_login_email, smtp_server, smtp_login_password, port, mailing_to_list

def update_domain_link_url(domain_link_url, domain_url_old):
    update_domain_link_url_db(domain_link_url, domain_url_old)

def update_final_table():
    update_final_table_db()

def detect_assignment_problem(domain, assignment_domain, external_link, external_anchor, problem):
    title = "assignment Problem Detected"
    data = get_mailing_info()
    gmailUser = data[0]
    smtp_server = data[1]
    gmailPassword = data[2]
    port = data[3]
    external_data = external_link_already_exists(external_link)
    external_id = external_data[0][0]
    if len(external_data) > 1:
        for item in external_data:
            if external_anchor == item[1]:
                external_id = item[0]
    assignment_id = get_assignment_id_by_assignment_domain(assignment_domain)[0]
    detection_date = get_today_date()

    import unicodedata
    external_anchor = unicodedata.normalize('NFKD', external_anchor).encode('ascii','ignore')

    for tmp_email in get_notification_emails_db(domain):
        message = """
        Hello %(name)s, crawler find out a link problem on %(domain_to_crawl)s,
        this link %(link)s" has been used - anchor %(anchor)s", but assigned domain url is %(assigned_domain)s
        """ % {"name":tmp_email[1], "domain_to_crawl":domain, "link":external_link, "anchor":external_anchor, "assigned_domain":assignment_domain[0]}
        recipient = tmp_email[0]
        send_email(gmailUser, gmailPassword, recipient, message, title, smtp_server, port)

        save_problem_db(external_id, assignment_id, detection_date, problem, recipient, "No")


def send_email(gmailUser, gmailPassword, recipient, message, title, smtp_server, port):
    print "Sending mail..........."
    msg = MIMEMultipart()
    msg['From'] = gmailUser
    msg['To'] = recipient
    msg['Subject'] = title
    msg.attach(MIMEText(message))

    mailServer = smtplib.SMTP(smtp_server, port)
    mailServer.ehlo()
    mailServer.starttls()
    mailServer.ehlo()
    mailServer.login(gmailUser, gmailPassword)
    mailServer.sendmail(gmailUser, recipient, msg.as_string())
    mailServer.close()
    print "Mail sent"

def status_problem(external_id, external_anchor, status, domain):
    title = "link response status Problem"
    data = get_mailing_info()
    gmailUser = data[0]
    smtp_server = data[1]
    gmailPassword = data[2]
    port = data[3]
    external_link = select_external_by_id(external_id)[0]

    detection_date = get_today_date()

    for tmp_email in get_notification_emails_db(domain):
        message = """
        Hello %(name)s, crawler find out a link problem on %(domain_to_crawl)s,
        this link "%(link)s" has %(response_status)s. Please check it.
        """ % {"name":tmp_email[1], "domain_to_crawl":domain, "link":external_link, "response_status":status}
        recipient = tmp_email[0]
        send_email(gmailUser, gmailPassword, recipient, message, title, smtp_server, port)

        save_problem_db(external_id, None, detection_date, status, recipient, "No")
