# -*- coding: utf-8 -*-

import datetime as dt
from django.http import Http404
from django.template.response import TemplateResponse
from django.core.paginator import Paginator, EmptyPage
from rpcz import RpcDeadlineExceeded

from core.python.search import Searcher, NotEnoughEntropy


def index(request):
  t = dt.datetime.now() - dt.timedelta(minutes=10)
  index_timestamp = {'iso': t.isoformat(), 'txt': 'no idea'}
  return TemplateResponse(request, 'index.html', {'index_timestamp': index_timestamp})

def search(request):
  query = request.GET.get('q', '')

  span_hilight = lambda w: '<span class="match">' + w + '</span>'

  try:
    searcher = Searcher(query, server='tcp://localhost:5550')
    results = searcher.results
    paginator = Paginator(results, 12)
    try:
      page = int(request.GET.get('page', 1))
      if page < 0: raise TypeError()
      page = paginator.page(page)
    except (TypeError, EmptyPage):
      raise Http404


    docs = [searcher.show_document(d, span_hilight) for d in page]
    corrected = map(lambda p: u'“' + p[0] + u'”', searcher.corrected)

    return TemplateResponse(request, 'results.html', {'query': query,
                                                      'documents': docs,
                                                      'page': page,
                                                      'count': len(searcher.results),
                                                      'timings': searcher.timings,
                                                      'corrected': corrected,
                                                     })
  except NotEnoughEntropy:
    return TemplateResponse(request, 'results.html', {'query': query,
                                                      'message': ("Bad query", "Your query does not contain enough entropy. Please, try something more interesting."),
                                                     })
  except RpcDeadlineExceeded:
    return TemplateResponse(request, 'results.html', {'query': query,
                                                      'message': ("We failed", "Index server seems to be unreachable. You might want to try again right now or, if it still isn't working, come back later."),
                                                     })
