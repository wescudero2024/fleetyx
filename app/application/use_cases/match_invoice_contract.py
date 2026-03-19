import re
from typing import Dict, List, Tuple
from difflib import SequenceMatcher


class MatchInvoiceContractUseCase:
    def __init__(self):
        self.similarity_threshold = 0.8

    def normalize_string(self, text: str) -> str:
        text = text.lower().strip()
        text = re.sub(r'[^\w\s]', '', text)
        text = re.sub(r'\s+', ' ', text)
        return text

    def calculate_similarity(self, str1: str, str2: str) -> float:
        str1_norm = self.normalize_string(str1)
        str2_norm = self.normalize_string(str2)
        
        return SequenceMatcher(None, str1_norm, str2_norm).ratio()

    def extract_company_components(self, company_name: str) -> List[str]:
        name = self.normalize_string(company_name)
        
        components = []
        
        words = name.split()
        for word in words:
            if len(word) > 2:
                components.append(word)
        
        if 'inc' in name:
            components.append('inc')
        if 'llc' in name:
            components.append('llc')
        if 'corp' in name or 'corporation' in name:
            components.append('corp')
        if 'co' in name or 'company' in name:
            components.append('co')
        
        return list(set(components))

    def find_best_match(
        self, 
        invoice_name: str, 
        contract_names: List[str]
    ) -> Tuple[str, float]:
        best_match = ""
        best_score = 0.0
        
        invoice_components = self.extract_company_components(invoice_name)
        
        for contract_name in contract_names:
            similarity = self.calculate_similarity(invoice_name, contract_name)
            
            contract_components = self.extract_company_components(contract_name)
            
            component_similarity = 0.0
            if invoice_components and contract_components:
                common_components = set(invoice_components) & set(contract_components)
                total_components = set(invoice_components) | set(contract_components)
                component_similarity = len(common_components) / len(total_components) if total_components else 0
            
            combined_score = (similarity * 0.7) + (component_similarity * 0.3)
            
            if combined_score > best_score:
                best_score = combined_score
                best_match = contract_name
        
        return best_match, best_score

    async def execute(
        self, 
        invoice_data: Dict[str, str], 
        contract_data: List[Dict[str, str]]
    ) -> Dict[str, any]:
        results = []
        
        contract_names = [contract.get('name', '') for contract in contract_data]
        
        for invoice_id, invoice_name in invoice_data.items():
            best_match, similarity_score = self.find_best_match(invoice_name, contract_names)
            
            is_match = similarity_score >= self.similarity_threshold
            
            results.append({
                'invoice_id': invoice_id,
                'invoice_name': invoice_name,
                'best_match': best_match,
                'similarity_score': similarity_score,
                'is_match': is_match,
                'confidence': 'high' if similarity_score >= 0.9 else 'medium' if similarity_score >= 0.8 else 'low'
            })
        
        return {
            'success': True,
            'data': {
                'matches': results,
                'total_processed': len(results),
                'high_confidence_matches': len([r for r in results if r['confidence'] == 'high']),
                'medium_confidence_matches': len([r for r in results if r['confidence'] == 'medium']),
                'low_confidence_matches': len([r for r in results if r['confidence'] == 'low']),
            }
        }
