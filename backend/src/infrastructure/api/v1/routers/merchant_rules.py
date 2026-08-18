from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID

from src.infrastructure.api.dependencies import get_manage_merchant_rules_use_case
from src.application.use_cases.manage_merchant_rules import ManageMerchantRulesUseCase
from src.infrastructure.api.v1.schemas.merchant_rule import MerchantRuleCreate, MerchantRuleResponse

router = APIRouter(prefix="/settings/merchant-rules", tags=["merchant-rules"])

@router.get("", response_model=List[MerchantRuleResponse])
async def list_rules(
    use_case: ManageMerchantRulesUseCase = Depends(get_manage_merchant_rules_use_case)
):
    """List all merchant regex categorization rules."""
    return await use_case.get_all_rules()

@router.post("", response_model=MerchantRuleResponse, status_code=status.HTTP_201_CREATED)
async def create_rule(
    data: MerchantRuleCreate,
    use_case: ManageMerchantRulesUseCase = Depends(get_manage_merchant_rules_use_case)
):
    """Create a new merchant regex categorization rule."""
    try:
        return await use_case.create_rule(
            pattern=data.pattern,
            category_id=data.category_id,
            priority=data.priority
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rule(
    rule_id: UUID,
    use_case: ManageMerchantRulesUseCase = Depends(get_manage_merchant_rules_use_case)
):
    """Delete a merchant regex categorization rule."""
    await use_case.delete_rule(rule_id)
