"""
UPDATE SCRIPT FOR ORDER-DETAIL.HTML
"""
import re

path = "api-gateway/templates/client/order-detail.html"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Fix canReviewItem
content = content.replace("const canReviewItem = canReview && itemType === 'book' && item.book_id;", "const canReviewItem = canReview && item.product_id;")

# Fix myReviewMap structure and lookups
content = content.replace("const existing = myReviewMap[String(item.book_id)] || null;", "const existing = myReviewMap[`${itemType}_${item.product_id}`] || null;")

# Fix button action
content = content.replace("submitItemReview(${item.book_id})", "submitItemReview('${itemType}', ${item.product_id})")

# Fix inputs
content = content.replace('id="review-rating-${item.book_id}"', 'id="review-rating-${itemType}-${item.product_id}"')
content = content.replace('id="review-comment-${item.book_id}"', 'id="review-comment-${itemType}-${item.product_id}"')

# Fix submitItemReview function
old_submit = """
        async function submitItemReview(bookId) {
"""
new_submit = """
        async function submitItemReview(productType, productId) {
"""
content = content.replace(old_submit, new_submit)

old_submit_rating = """
            const ratingEl = document.getElementById(`review-rating-${bookId}`);
            const commentEl = document.getElementById(`review-comment-${bookId}`);
"""
new_submit_rating = """
            const ratingEl = document.getElementById(`review-rating-${productType}-${productId}`);
            const commentEl = document.getElementById(`review-comment-${productType}-${productId}`);
"""
content = content.replace(old_submit_rating, new_submit_rating)

# Find the fetch POST for review
content = re.sub(
    r"body: JSON\.stringify\(\{ book_id: bookId, rating, comment \}\)",
    "body: JSON.stringify({ product_type: productType, product_id: productId, rating, comment })",
    content
)

# Fix loadMyReviewMap
old_load_map = """
                return data.reduce((acc, review) => {
                    acc[String(review.book_id)] = review;
                    return acc;
                }, {});
"""
new_load_map = """
                return data.reduce((acc, review) => {
                    acc[`${review.product_type}_${review.product_id}`] = review;
                    return acc;
                }, {});
"""
content = content.replace(old_load_map, new_load_map)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("done")
