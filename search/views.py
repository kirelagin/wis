# -*- coding: utf-8 -*-

import datetime as dt
from django.http import Http404
from django.template.response import TemplateResponse

import core.python.search as srch


def index(request):
  t = dt.datetime.now() - dt.timedelta(minutes=10)
  index_timestamp = {'iso': t.isoformat(), 'txt': 'no idea'}
  return TemplateResponse(request, 'index.html', {'index_timestamp': index_timestamp})

def search(request):
  query = request.GET.get('q')
  if not query: raise Http404

  span_hilight = lambda w: '<span class="match">' + w + '</span>'

  ans = srch.search(query)
  rendered = srch.show_documents(ans.postings, span_hilight)

  docs = rendered.docs

  return TemplateResponse(request, 'results.html', {'query': query,
                                                    'documents': docs,
                                                    'num_keywords': ans.num_keywords,
                                                    'num_positions': ans.num_positions,
                                                    'query_time': ans.query_time,
                                                    'proc_time': ans.proc_time,
                                                    'render_time': rendered.render_time})
