from flask import Blueprint, request
from .models import Supplier
from . import db
from .schemas import supplier_to_dict
from .utils import role_required, Response, ValidationError, NotFoundError

bp = Blueprint('suppliers', __name__)

@bp.route('', methods=['POST'])
@role_required(['admin', 'stock_operator', 'purchaser'])
def create_supplier():
    data = request.json or {}
    supplier_name = data.get('supplier_name')
    contact_info = data.get('contact_info')
    
    if not supplier_name:
        raise ValidationError('Supplier name is required')
    
    # 检查供应商名称是否已存在
    if Supplier.query.filter_by(supplier_name=supplier_name).first():
        raise ValidationError('Supplier name already exists')
    
    supplier = Supplier(
        supplier_name=supplier_name,
        contact_info=contact_info
    )
    
    db.session.add(supplier)
    db.session.commit()
    
    return Response.success({
        'supplier_id': supplier.supplier_id,
        'supplier_name': supplier.supplier_name
    })

@bp.route('', methods=['GET'])
def list_suppliers():
    suppliers = Supplier.query.all()
    result = [supplier_to_dict(supplier) for supplier in suppliers]
    return Response.success(result)

@bp.route('/<int:supplier_id>', methods=['GET'])
def get_supplier(supplier_id):
    supplier = Supplier.query.get(supplier_id)
    if not supplier:
        raise NotFoundError('Supplier not found')
    return Response.success(supplier_to_dict(supplier))

@bp.route('/<int:supplier_id>', methods=['PUT'])
@role_required(['admin', 'stock_operator', 'purchaser'])
def update_supplier(supplier_id):
    supplier = Supplier.query.get(supplier_id)
    if not supplier:
        raise NotFoundError('Supplier not found')
    
    data = request.json or {}
    supplier_name = data.get('supplier_name')
    contact_info = data.get('contact_info')
    
    if supplier_name:
        if supplier_name != supplier.supplier_name:
            # 检查新的供应商名称是否已存在
            if Supplier.query.filter_by(supplier_name=supplier_name).first():
                raise ValidationError('Supplier name already exists')
        supplier.supplier_name = supplier_name
    
    if contact_info is not None:
        supplier.contact_info = contact_info
    
    db.session.commit()
    
    return Response.success(supplier_to_dict(supplier))

@bp.route('/<int:supplier_id>', methods=['DELETE'])
@role_required(['admin'])
def delete_supplier(supplier_id):
    supplier = Supplier.query.get(supplier_id)
    if not supplier:
        raise NotFoundError('Supplier not found')
    
    # 检查是否有商品关联到该供应商
    if supplier.products:
        raise ValidationError('Cannot delete supplier with associated products')
    
    db.session.delete(supplier)
    db.session.commit()
    
    return Response.success({'supplier_id': supplier_id})
