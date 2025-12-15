from flask import Blueprint, request
from .models import Category
from . import db
from .schemas import category_to_dict
from .utils import role_required, Response, ValidationError, NotFoundError

bp = Blueprint('categories', __name__)

@bp.route('', methods=['POST'])
@role_required(['admin', 'stock_operator'])
def create_category():
    data = request.json or {}
    category_name = data.get('category_name')
    description = data.get('description')
    
    if not category_name:
        raise ValidationError('Category name is required')
    
    # 检查分类名称是否已存在
    if Category.query.filter_by(category_name=category_name).first():
        raise ValidationError('Category name already exists')
    
    category = Category(
        category_name=category_name,
        description=description
    )
    
    db.session.add(category)
    db.session.commit()
    
    return Response.success({
        'category_id': category.category_id,
        'category_name': category.category_name
    })

@bp.route('', methods=['GET'])
def list_categories():
    categories = Category.query.all()
    result = [category_to_dict(category) for category in categories]
    return Response.success(result)

@bp.route('/<int:category_id>', methods=['GET'])
def get_category(category_id):
    category = Category.query.get(category_id)
    if not category:
        raise NotFoundError('Category not found')
    return Response.success(category_to_dict(category))

@bp.route('/<int:category_id>', methods=['PUT'])
@role_required(['admin', 'stock_operator'])
def update_category(category_id):
    category = Category.query.get(category_id)
    if not category:
        raise NotFoundError('Category not found')
    
    data = request.json or {}
    category_name = data.get('category_name')
    description = data.get('description')
    
    if category_name:
        if category_name != category.category_name:
            # 检查新的分类名称是否已存在
            if Category.query.filter_by(category_name=category_name).first():
                raise ValidationError('Category name already exists')
        category.category_name = category_name
    
    if description is not None:
        category.description = description
    
    db.session.commit()
    
    return Response.success(category_to_dict(category))

@bp.route('/<int:category_id>', methods=['DELETE'])
@role_required(['admin'])
def delete_category(category_id):
    category = Category.query.get(category_id)
    if not category:
        raise NotFoundError('Category not found')
    
    # 检查是否有商品关联到该分类
    if category.products:
        raise ValidationError('Cannot delete category with associated products')
    
    db.session.delete(category)
    db.session.commit()
    
    return Response.success({'category_id': category_id})
