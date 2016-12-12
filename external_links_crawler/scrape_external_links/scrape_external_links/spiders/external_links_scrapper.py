# -*- coding: utf-8 -*-
import scrapy
from scrape_external_links.helpers import *
from scrape_external_links.items import ScrapeExternalLinksItem
from scrapy import signals
from scrapy.xlib.pydispatch import dispatcher
from urlparse import urlparse
from scrapy.utils.markup import remove_tags

class ExternalLinksScrapperSpider(scrapy.Spider):
    name = "external_links_scrapper"
    handle_httpstatus_list = range(300, 510)

    def __init__(self):
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    def spider_closed(self, spider, reason):

        # second param is instance of spder about to be closed.
        if reason == "finished":
            make_domain_working_done()
            update_final_table()
        else:
            make_domain_working_error()
            data = get_mailing_info()
            gmailUser = data[0]
            gmailPassword = data[2]
            recipient = data[4][0]
            smtp_server = data[1]
            port = data[3]
            title = "external links crawler crashed"
            message = """
                  Hi, an ERROR happened in external_links_scrapper and the reason is %s \nYou just need to run it again and it will continue automatically
                  """ % (reason,)
            send_email(gmailUser, gmailPassword, recipient, message, title, smtp_server, port)





    def start_requests(self):
        if check_fresh_crawler():
            clean_onprogress_tables()
            domains = init_onprogress_domain()
            if len(domains) < 1:
                print "No domains to be scrapped"
                return
            domain = domains[0]
            update_domain_ip_address(domain)
            update_last_crawled_date(domain)
            insert_into_onprogress_pages([domain], domain)
            make_domain_scrapped(domain)
            yield scrapy.Request(domain, callback= self.parse_home_page)
        else:
            print "no fresh----------------------------------------------------------------------------"
            x,y,z = prepare_to_continue_scrapper()
            domain = z[0]
            pages = is_pages_to_be_scrapped(domain)
            if pages is not None:
                for page in pages:
                    yield scrapy.Request(page[0], self.parse_page)

    def parse_home_page(self,response):
        if response.status > 300:
            if response.status == 301:
                domain_url = urlparse(response.url).netloc
                if domain_url.startswith("www"):
                    domain_link_url = "http://" + domain_url[4:] + "/"
                else:
                    domain_link_url = "http://www." + domain_url + "/"
                update_domain_link_url(domain_link_url, response.url)
                yield scrapy.Request(domain_link_url, self.parse_home_page)
            #Detect if site is not responding, if so, save this event into database
            #make domain status down
            domain = get_domain_by_pageUrl(response.url)[0]
            change_domain_status_to_down(domain)
            return
        internal_urls = []
        external_urls = []
        status_urls = []
        anchors = []
        print 'response.url-----------------------------------------------------------------------------'
        print response.url
        print '-----------------------------------------------------------------------------'
        domain = get_domain_by_pageUrl(response.url)[0]
        print '-----------------------------------------------------------------------------'
        print domain
        print '-----------------------------------------------------------------------------'
        for a_tag in response.xpath('//a'):
            url = response.urljoin(a_tag.xpath('@href').extract_first())
            if check_url(url):
                if internal_or_external(url, domain):
                    internal_urls.append(url)
                else:
                    external_urls.append(url)
                    anchor = remove_tags(a_tag.extract())

                    #anchor =  a_tag.xpath('text()').extract_first()
                    if anchor is None:
                        anchor = ''
                    anchors.append(anchor)
                    status_url = 'follow'
                    if  a_tag.xpath('@rel').extract_first() == 'nofollow':
                        status_url = 'nofollow'
                    status_urls.append(status_url)
        update_waiting_list(internal_urls, domain)
        item_scrapped = ScrapeExternalLinksItem()
        item_scrapped["page_url"] = response.url
        item_scrapped["internal_links"] ={}
        item_scrapped["external_links"] = {}
        item_scrapped["link_type"] = {}
        item_scrapped["link_anchor"] = {}
        index = 0
        for link in internal_urls:
            item_scrapped["internal_links"][index] = link
            index += 1
        index = 0
        for link in external_urls:
            item_scrapped["external_links"][index] = link
            index += 1
        index = 0
        for status in status_urls:
            item_scrapped["link_type"][index] = status
            index += 1
        index = 0
        for anchor in anchors:
            item_scrapped["link_anchor"][index] = anchor
            index += 1
        make_page_scrapped(response.url)
        #########################################################################
        page_id = save_url_to_domainPages(item_scrapped["page_url"])
        save_external_links(item_scrapped["external_links"], page_id, item_scrapped["link_anchor"], item_scrapped["link_type"])
        #update domain_pages(outband_links_count)
        update_outband_links_count(len(item_scrapped["external_links"]), page_id)
        #taking care of assignments and domains links count
        domain_id = get_domain_id_by_page_url(item_scrapped["page_url"])[0]

        if item_scrapped["page_url"] == get_domain_by_pageUrl(item_scrapped["page_url"])[0]:
            update_source_page(item_scrapped["page_url"])

        all_assignment_domains = get_all_assignment_domains()
        for assignment_domain in all_assignment_domains:
            for external_key, external_link in item_scrapped["external_links"].items():
                if assignment_domain[0] in external_link:
                    save_assignment_domain(domain_id, assignment_domain)
                else:
                    assignment_url = urlparse(assignment_domain[0]).netloc
                    if assignment_url.startswith('www'):
                        assignment_url = assignment_url[4:]
                    if assignment_url in external_link:
                        #Detect problem
                        problem = "www"
                        if "https" in assignment_domain and "https" not in external_link:
                            problem = "http"
                        if "https" not in assignment_domain and "https" in external_link:
                            problem = "http"
                        detect_assignment_problem(domain, assignment_domain, external_link, item_scrapped["link_anchor"][external_key], problem)
                        save_assignment_domain(domain_id, assignment_domain)
        update_assignments_links_count()
        update_domains_assignments_count()
        update_external_link_on_page(page_id)
        ############################################################################
        yield item_scrapped
        pages = is_pages_to_be_scrapped(domain)
        if pages is not None:
            for page in pages:
                yield scrapy.Request(page[0], self.parse_page)
        for link in external_urls:
            request = scrapy.Request(str(link.encode('utf8')), self.parse_external_link)
            request.meta['id'] = external_link_already_exists(str(link.encode('utf8')))
            request.meta['domain'] = domain
            yield request

    def parse_page(self, response):
        internal_urls = []
        external_urls = []
        status_urls = []
        anchors = []
        domain = get_domain_by_pageUrl(response.url)[0]
        print '-----------------------------------------------------------------------------'
        print domain
        print '-----------------------------------------------------------------------------'
        for a_tag in response.xpath('//a'):
            url = response.urljoin(a_tag.xpath('@href').extract_first())
            if check_url(url):
                if internal_or_external(url, domain):
                    internal_urls.append(url)
                else:
                    external_urls.append(url)
                    anchor = remove_tags(a_tag.extract())
                    #anchor =  a_tag.xpath('text()').extract_first()
                    if anchor is None:
                        anchor = ''
                    anchors.append(anchor)
                    status_url = 'follow'
                    if  a_tag.xpath('@rel').extract_first() == 'nofollow':
                        status_url = 'nofollow'
                    status_urls.append(status_url)
        update_waiting_list(internal_urls, domain)
        item_scrapped = ScrapeExternalLinksItem()
        item_scrapped["page_url"] = response.url
        item_scrapped["internal_links"] ={}
        item_scrapped["external_links"] = {}
        item_scrapped["link_type"] = {}
        item_scrapped["link_anchor"] = {}
        index = 0
        for link in internal_urls:
            item_scrapped["internal_links"][index] = link
            index += 1
        index = 0
        for link in external_urls:
            item_scrapped["external_links"][index] = link
            index += 1
        index = 0
        for status in status_urls:
            item_scrapped["link_type"][index] = status
            index += 1
        index = 0
        for anchor in anchors:
            item_scrapped["link_anchor"][index] = anchor
            index += 1
        make_page_scrapped(response.url)
        #########################################################################
        page_id = save_url_to_domainPages(item_scrapped["page_url"])
        save_external_links(item_scrapped["external_links"], page_id, item_scrapped["link_anchor"], item_scrapped["link_type"])
        #update domain_pages(outband_links_count)
        update_outband_links_count(len(item_scrapped["external_links"]), page_id)
        #taking care of assignments and domains links count
        domain_id = get_domain_id_by_page_url(item_scrapped["page_url"])[0]

        if item_scrapped["page_url"] == get_domain_by_pageUrl(item_scrapped["page_url"])[0]:
            update_source_page(item_scrapped["page_url"])

        all_assignment_domains = get_all_assignment_domains()
        all_assignment_domains = get_all_assignment_domains()
        for assignment_domain in all_assignment_domains:
            for external_key, external_link in item_scrapped["external_links"].items():
                if assignment_domain[0] in external_link:
                    save_assignment_domain(domain_id, assignment_domain)
                else:
                    assignment_url = urlparse(assignment_domain[0]).netloc
                    if assignment_url.startswith('www'):
                        assignment_url = assignment_url[4:]
                    if assignment_url in external_link:
                        #Detect problem
                        problem = "www"
                        if "https" in assignment_domain and "https" not in external_link:
                            problem = "http"
                        if "https" not in assignment_domain and "https" in external_link:
                            problem = "http"
                        detect_assignment_problem(domain, assignment_domain, external_link, item_scrapped["link_anchor"][external_key], problem)
                        save_assignment_domain(domain_id, assignment_domain)
        update_assignments_links_count()
        update_domains_assignments_count()
        update_external_link_on_page(page_id)
        ############################################################################
        yield item_scrapped
        pages = is_pages_to_be_scrapped(domain)
        if pages is not None:
            for page in pages:
                yield scrapy.Request(page[0], self.parse_page)
        for link in external_urls:
            request = scrapy.Request(str(link.encode('utf8')), self.parse_external_link)
            request.meta['id'] = external_link_already_exists(str(link))
            request.meta['domain'] = domain
            yield request


    def parse_external_link(self, response):
        status = response.status
        if status is None:
            status = 404
        print "----------------------------------response.meta['id']----------------------------------------------"
        print response.meta['id']
        print "-------------------------------------response.meta['id']-------------------------------------------"
        for tmp in response.meta['id']:
            if status != 200:
                status_problem(tmp[0], tmp[1], status, response.meta['domain'])
            save_external_link_state(tmp[0], status)

    def process_exception(self, response, exception, spider):
        print "Sending mail..........."
        import smtplib
        from email.MIMEMultipart import MIMEMultipart
        from email.MIMEText import MIMEText

        #smtp_login_email, smtp_server, smtp_login_password, port, mailing_to_list
        data = get_mailing_info()
        gmailUser = data[0]
        gmailPassword = data[2]
        recipient = data[4]
        title = "external links crawler crashed"
        ex_class = "%s.%s" % (exception.__class__.__module__,  exception.__class__.__name__)
        message = """
                Hi, an ERROR happened in %s while processing the url %s and the response status is %s
                """ % (ex_class, response.url, response.status)

        msg = MIMEMultipart()
        msg['From'] = gmailUser
        msg['To'] = recipient
        msg['Subject'] = title
        msg.attach(MIMEText(message))

        mailServer = smtplib.SMTP(data[1], data[3])
        mailServer.ehlo()
        mailServer.starttls()
        mailServer.ehlo()
        mailServer.login(gmailUser, gmailPassword)
        mailServer.sendmail(gmailUser, recipient, msg.as_string())
        mailServer.close()
        print "Mail sent"
