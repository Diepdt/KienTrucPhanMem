"""
UPDATE SCRIPT FOR COMMENT RATE SERVICE VIEWS.PY AND URLS.PY
"""
import re

views_path = "comment-rate-service/comment/views.py"
with open(views_path, "r", encoding="utf-8") as f:
    views_content = f.read()

# Replace has_customer_purchased_book
new_has_purchased = """
def has_customer_purchased_product(customer_id, product_type, product_id):
    try:
        resp = http_requests.get(
            f"{django_settings.ORDER_SERVICE_URL}/api/orders/customer/{customer_id}/internal/",
            timeout=5
        )
        if resp.status_code != 200:
            return False

        orders = resp.json() if isinstance(resp.json(), list) else []
        for order in orders:
            if order.get('status') != 'delivered':
                continue
            for item in order.get('items', []):
                # Backwards compat & standard behavior
                it_pt = item.get('product_type', 'book')
                if it_pt == product_type and int(item.get('product_id', 0)) == int(product_id):
                    return True
    except Exception as e:
        logger.error(f"has_customer_purchased_product error: {e}")

    return False
"""
views_content = re.sub(
    r"def has_customer_purchased_book\(customer_id, book_id\):[\s\S]*?return False",
    new_has_purchased.strip(),
    views_content
)

# Replace CreateReviewView 
new_create = """
class CreateReviewView(APIView):
    \"\"\"Khách hàng dánh giá s?n ph?m.\"\"\"

    def post(self, request):
        auth = request.headers.get('Authorization', '')
        valid, customer = verify_customer_token(auth)
        if not valid:
            return Response({'error': 'Unauthorized'}, status=401)

        product_type = request.data.get('product_type', 'book')
        product_id = request.data.get('product_id')
        rating = request.data.get('rating')
        comment = request.data.get('comment', '')

        if not product_id or rating is None:
            return Response({'error': 'product_id và rating b?t bu?c'}, status=400)

        if not has_customer_purchased_product(customer['id'], product_type, product_id):
            return Response({'error': 'B?n ch? có th? dánh giá s?n ph?m trong don hàng dã giao.'}, status=403)

        review, created = Review.objects.update_or_create(
            customer_id=customer['id'],
            product_type=product_type,
            product_id=product_id,
            defaults={'rating': int(rating), 'comment': comment}
        )
        action = 'Ðánh giá dã du?c t?o.' if created else 'Ðánh giá dã du?c c?p nh?t.'
        return Response({
            'message': action,
            'review': ReviewSerializer(review).data
        }, status=201 if created else 200)
"""
views_content = re.sub(
    r"class CreateReviewView\(APIView\):[\s\S]*?(?=class AdminReviewListView)",
    new_create.strip() + "\n\n\n",
    views_content
)

# AdminReviewListView 
new_admin_list = """
class AdminReviewListView(APIView):
    \"\"\"Manager/Staff xem th?ng kê và danh sách dánh giá.\"\"\"

    def get(self, request):
        auth = request.headers.get('Authorization', '')
        valid, _admin = verify_admin_token(auth)
        if not valid:
            return Response({'error': 'Unauthorized'}, status=401)

        reviews = Review.objects.all().order_by('-created_at')
        stats = reviews.aggregate(avg_rating=Avg('rating'), total=Count('id'))

        distribution = {str(i): reviews.filter(rating=i).count() for i in range(1, 6)}

        top_products_qs = (
            Review.objects.values('product_type', 'product_id')
            .annotate(avg_rating=Avg('rating'), total_reviews=Count('id'))
            .order_by('-avg_rating', '-total_reviews')[:10]
        )

        return Response({
            'summary': {
                'total_reviews': stats['total'] or 0,
                'avg_rating': round(stats['avg_rating'] or 0, 2),
                'rating_distribution': distribution,
            },
            'top_products': list(top_products_qs),
            'results': ReviewSerializer(reviews, many=True).data,
        })
"""
views_content = re.sub(
    r"class AdminReviewListView\(APIView\):[\s\S]*?(?=class AdminReviewDetailView)",
    new_admin_list.strip() + "\n\n\n",
    views_content
)

# BookReviewListView -> ProductReviewListView
new_product_review = """
class ProductReviewListView(APIView):
    \"\"\"Danh sách dánh giá c?a m?t s?n ph?m.\"\"\"

    def get(self, request, product_type, product_id):
        reviews = Review.objects.filter(product_type=product_type, product_id=product_id).order_by('-created_at')
        stats = reviews.aggregate(avg_rating=Avg('rating'), total=Count('id'))
        return Response({
            'product_type': product_type,
            'product_id': product_id,
            'avg_rating': round(stats['avg_rating'] or 0, 2),
            'total_reviews': stats['total'],
            'reviews': ReviewSerializer(reviews, many=True).data
        })
"""
views_content = re.sub(
    r"class BookReviewListView\(APIView\):[\s\S]*?(?=class CustomerReviewListView)",
    new_product_review.strip() + "\n\n\n",
    views_content
)

# BookAvgRatingView -> ProductAvgRatingView
new_avg_rating = """
class ProductAvgRatingView(APIView):
    \"\"\"API n?i b?: l?y di?m trung bình c?a nhi?u s?n ph?m.\"\"\"

    def get(self, request):
        \"\"\"GET /api/reviews/avg-ratings/?product_type=book&product_ids=1,2,3\"\"\"
        product_ids_str = request.query_params.get('product_ids', '')
        # Fallback to book_ids
        if not product_ids_str:
            product_ids_str = request.query_params.get('book_ids', '')

        if not product_ids_str:
            return Response({'error': 'product_ids b?t bu?c'}, status=400)
            
        product_type = request.query_params.get('product_type', 'book')
        
        try:
            ids = [int(b) for b in product_ids_str.split(',')]
        except ValueError:
            return Response({'error': 'product_ids không h?p l?'}, status=400)

        result = {}
        for p_id in ids:
            stats = Review.objects.filter(product_type=product_type, product_id=p_id).aggregate(
                avg=Avg('rating'), count=Count('id'))
            result[p_id] = {
                'avg_rating': round(stats['avg'] or 0, 2),
                'count': stats['count']
            }
        return Response(result)
"""
views_content = re.sub(
    r"class BookAvgRatingView\(APIView\):[\s\S]*",
    new_avg_rating.strip() + "\n",
    views_content
)

with open(views_path, "w", encoding="utf-8") as f:
    f.write(views_content)


# Now update urls.py
urls_path = "comment-rate-service/comment/urls.py"
with open(urls_path, "r", encoding="utf-8") as f:
    urls_content = f.read()

urls_content = urls_content.replace('BookReviewListView,', 'ProductReviewListView,\n                    ')
urls_content = urls_content.replace('BookAvgRatingView,', 'ProductAvgRatingView,')

new_internal = """
class AllReviewsInternalView(APIView):
    \"\"\"Tr? v? t?t c? review - ch? dành cho recommender-service g?i n?i b?.\"\"\"
    def get(self, request):
        reviews = Review.objects.all().values('customer_id', 'product_type', 'product_id', 'rating')
        # Map product_id to book_id just for backward compatibility if needed,
        # but since we're using recommender service that expects 'book_id', let's format it.
        results = []
        for r in reviews:
            if r['product_type'] == 'book':
                r['book_id'] = r['product_id']
                results.append(r)
        return Response(results)
"""
urls_content = re.sub(
    r"class AllReviewsInternalView\(APIView\):[\s\S]*?(?=urlpatterns = \[)",
    new_internal.strip() + "\n\n",
    urls_content
)

urls_content = urls_content.replace(
    "path('reviews/books/<int:book_id>/', BookReviewListView.as_view(), name='book-reviews'),",
    "path('reviews/product/<str:product_type>/<int:product_id>/', ProductReviewListView.as_view(), name='product-reviews'),\n    path('reviews/books/<int:product_id>/', ProductReviewListView.as_view(), kwargs={'product_type': 'book'}, name='book-reviews'),"
)
urls_content = urls_content.replace(
    "path('reviews/avg-ratings/', BookAvgRatingView.as_view(), name='avg-ratings'),",
    "path('reviews/avg-ratings/', ProductAvgRatingView.as_view(), name='avg-ratings'),"
)

with open(urls_path, "w", encoding="utf-8") as f:
    f.write(urls_content)

print("Updated views.py and urls.py")
