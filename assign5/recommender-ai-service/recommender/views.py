from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import logging

from .models import Recommendation
from .behavior_model.inference import get_inference_engine

logger = logging.getLogger(__name__)


class RecommendationsView(APIView):
    """Gợi ý đa sản phẩm (AI Behavior Model) cho khách hàng."""

    def get(self, request, customer_id):
        engine = get_inference_engine()
        recommendations = engine.recommend(customer_id, top_k=10)

        # Nếu engine trả về mảng rỗng (VD: chưa có pretrained model/data) thì fallback đơn giản
        if not recommendations:
            recommendations = []

        # Lưu cache vào DB
        Recommendation.objects.filter(customer_id=customer_id).delete()
        
        saved_recs = []
        for rec in recommendations:
            obj = Recommendation.objects.create(
                customer_id=customer_id,
                service_type=rec.get('service_type', 'book'),
                product_id=rec.get('product_id', 0),
                score=rec.get('score', 0.0),
                reason=f"AI Confidence: {rec.get('confidence', 0.0):.2%}"
            )
            saved_recs.append({
                'service_type': obj.service_type,
                'product_id': obj.product_id,
                'score': round(obj.score, 4),
                'reason': obj.reason
            })

        return Response({
            'customer_id': customer_id,
            'total': len(saved_recs),
            'recommendations': saved_recs
        })


class CachedRecommendationsView(APIView):
    """Lấy gợi ý đã được cache."""

    def get(self, request, customer_id):
        recs = Recommendation.objects.filter(customer_id=customer_id).order_by('-score')
        if not recs.exists():
            # Tính lại nếu chưa có cache
            return RecommendationsView().get(request, customer_id)
        
        data = [
            {
                'service_type': r.service_type,
                'product_id': r.product_id,
                'score': round(r.score, 4),
                'reason': r.reason
            } for r in recs
        ]
        return Response({'customer_id': customer_id, 'total': len(data), 'recommendations': data})
