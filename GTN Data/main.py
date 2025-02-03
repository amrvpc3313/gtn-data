from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
import csv
import os
from functions import *

def home(request):
    return render(request, 'scraper/home.html')
def scrape(request):
    if request.method == 'POST':
        asins = request.POST.get('asins', '').split(',')
        asins = [asin.strip() for asin in asins if asin.strip()]
        
        asin_file = request.FILES.get('asin_file')
        if asin_file:
            lines = asin_file.read().decode('utf-8').splitlines()
            if lines and lines[0].strip().lower() == 'asin':
                asins.extend(line.strip() for line in lines[1:] if line.strip())
            else:
                return JsonResponse({'error': "TXT file must start with a header 'ASIN'."}, status=400)
        
        if not asins:
            return JsonResponse({'error': 'Please provide at least one ASIN.'}, status=400)
        
        scraped_data = scrape_amazon_asins(asins)
        
        if 'download' in request.POST:
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename=scraped_data.csv'
            writer = csv.writer(response)
            writer.writerow(scraped_data[0].keys())
            for row in scraped_data:
                writer.writerow(row.values())
            return response
        
        return JsonResponse({'data': scraped_data})
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)