"""
Module for mapping Article and Sub-Article fields to Categories.
Модуль для преобразования полей Статья и Подстатья в Категорию.
"""
import json
import logging
import os
from typing import Dict, Optional

from core.config import settings

logger = logging.getLogger(__name__)


class CategoryMapper:
    """
    Class for mapping Article and Sub-Article fields to Categories
    according to the mapping table from the specification.
    
    Класс для преобразования полей Статья и Подстатья в Категорию
    согласно таблице соответствия из ТЗ.
    """
    
    def __init__(self, mapping_file_path: Optional[str] = None):
        """
        Initialize the CategoryMapper with a mapping file path.
        
        Args:
            mapping_file_path: Path to the JSON file with category mapping.
                              If None, uses the path from settings.
        """
        self.mapping_file_path = mapping_file_path or settings.CATEGORY_MAPPING_PATH
        self.mapping: Dict[str, Dict[str, str]] = self._load_mapping()
        
    def _load_mapping(self) -> Dict[str, Dict[str, str]]:
        """
        Load the category mapping from the JSON file.
        
        Returns:
            Dict[str, Dict[str, str]]: Dictionary with article and sub-article to category mapping
        """
        try:
            if not os.path.exists(self.mapping_file_path):
                logger.warning(f"Category mapping file not found: {self.mapping_file_path}")
                return {}
                
            with open(self.mapping_file_path, 'r', encoding='utf-8') as f:
                mapping = json.load(f)
                logger.info(f"Successfully loaded category mapping with {len(mapping)} articles")
                return mapping
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Error loading category mapping file: {e}")
            return {}
    
    def map_category(self, article: str, sub_article: str) -> str:
        """
        Map article and sub-article to a category according to the mapping table.
        
        Args:
            article: Article field value
            sub_article: Sub-article field value
            
        Returns:
            str: Mapped category or fallback value if mapping not found
        """
        if not article or not sub_article:
            logger.warning(f"Empty article or sub-article: '{article}', '{sub_article}'")
            return "Не определено"
            
        # Try to find the mapping
        try:
            if article in self.mapping and sub_article in self.mapping[article]:
                return self.mapping[article][sub_article]
            else:
                logger.warning(f"No mapping found for article '{article}' and sub-article '{sub_article}'")
                return "Прочее"
        except Exception as e:
            logger.error(f"Error mapping category for '{article}' and '{sub_article}': {e}")
            return "Прочее"
    
    def reload_mapping(self) -> bool:
        """
        Reload the category mapping from the file.
        
        Returns:
            bool: True if reloading was successful, False otherwise
        """
        try:
            self.mapping = self._load_mapping()
            return bool(self.mapping)
        except Exception as e:
            logger.error(f"Error reloading category mapping: {e}")
            return False


# Create a singleton instance for easy import and use
category_mapper = CategoryMapper()


def map_category(article: str, sub_article: str) -> str:
    """
    Convenience function to map article and sub-article to a category.
    
    Args:
        article: Article field value
        sub_article: Sub-article field value
        
    Returns:
        str: Mapped category
    """
    return category_mapper.map_category(article, sub_article)
