from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Optional
from datetime import datetime
import os
from PIL import Image, ImageTk

class Season(Enum):
    WINTER = "зима"
    SPRING = "весна"
    SUMMER = "лето"
    AUTUMN = "осень"

class ClothingType(Enum):
    OUTERWEAR = "верхняя одежда"
    UNDERWEAR = "нижнее белье"
    PANTS_SHORTS = "штаны/шорты"
    TOP = "верхняя нательная одежда"
    MENS_SET = "комплекты муж"
    WOMENS_SET = "комплекты жен"

class Clothing(ABC):
    def __init__(self, name: str, size: str, color: str, material: str, price: float, image_path: str = None):
        self.name = name
        self.size = size
        self.color = color
        self.material = material
        self.price = price
        self.image_path = image_path
        self.production_date = datetime.now()

    @abstractmethod
    def get_season(self) -> Season:
        pass

    @abstractmethod
    def get_type(self) -> ClothingType:
        pass

    def get_image(self, size: tuple = (100, 100)) -> Optional[ImageTk.PhotoImage]:
        if self.image_path and os.path.exists(self.image_path):
            try:
                image = Image.open(self.image_path)
                image = image.resize(size, Image.Resampling.LANCZOS)
                return ImageTk.PhotoImage(image)
            except Exception as e:
                print(f"Ошибка загрузки изображения: {e}")
        return None

    def __str__(self) -> str:
        return f"{self.name} - Размер: {self.size}, Цвет: {self.color}, Материал: {self.material}, Цена: {self.price}"

class Outerwear(Clothing):
    def get_season(self) -> Season:
        return Season.WINTER

    def get_type(self) -> ClothingType:
        return ClothingType.OUTERWEAR

class Underwear(Clothing):
    def get_season(self) -> Season:
        return Season.SUMMER

    def get_type(self) -> ClothingType:
        return ClothingType.UNDERWEAR

class PantsShorts(Clothing):
    def get_season(self) -> Season:
        return Season.SUMMER

    def get_type(self) -> ClothingType:
        return ClothingType.PANTS_SHORTS

class Top(Clothing):
    def get_season(self) -> Season:
        return Season.SUMMER

    def get_type(self) -> ClothingType:
        return ClothingType.TOP

class MensSet(Clothing):
    def get_season(self) -> Season:
        return Season.SUMMER

    def get_type(self) -> ClothingType:
        return ClothingType.MENS_SET

class WomensSet(Clothing):
    def get_season(self) -> Season:
        return Season.SUMMER

    def get_type(self) -> ClothingType:
        return ClothingType.WOMENS_SET

class ClothingFactory:
    def __init__(self):
        self.inventory: List[Clothing] = []
        self.market_trends: List[str] = []

    def add_clothing(self, clothing: Clothing) -> None:
        self.inventory.append(clothing)

    def add_market_trend(self, trend: str) -> None:
        self.market_trends.append(trend)

    def get_clothing_by_season(self, season: Season) -> List[Clothing]:
        return [clothing for clothing in self.inventory if clothing.get_season() == season]

    def get_clothing_by_type(self, clothing_type: ClothingType) -> List[Clothing]:
        return [clothing for clothing in self.inventory if clothing.get_type() == clothing_type]

    def get_current_market_trends(self) -> List[str]:
        return self.market_trends

    def get_inventory_value(self) -> float:
        return sum(clothing.price for clothing in self.inventory)

# Пример использования
if __name__ == "__main__":
    factory = ClothingFactory()

    # Добавляем одежду в инвентарь
    jacket = Outerwear("Теплая куртка", "L", "черный", "нейлон", 5000.0)
    tshirt = Top("Футболка", "M", "белый", "хлопок", 1000.0)
    pants = PantsShorts("Джинсы", "L", "синий", "деним", 3000.0)
    underwear = Underwear("Трусы", "M", "серый", "хлопок", 500.0)
    mens_set = MensSet("Спортивный костюм", "XL", "синий", "хлопок", 4000.0)
    womens_set = WomensSet("Пижамный комплект", "M", "розовый", "шелк", 3500.0)

    factory.add_clothing(jacket)
    factory.add_clothing(tshirt)
    factory.add_clothing(pants)
    factory.add_clothing(underwear)
    factory.add_clothing(mens_set)
    factory.add_clothing(womens_set)

    # Добавляем рыночные тренды
    factory.add_market_trend("Экологичные материалы в тренде")
    factory.add_market_trend("Минималистичный дизайн популярен")

    # Выводим одежду по сезону
    print("Летняя одежда:")
    for clothing in factory.get_clothing_by_season(Season.SUMMER):
        print(clothing)

    print("\nТекущие рыночные тренды:")
    for trend in factory.get_current_market_trends():
        print(f"- {trend}")

    print(f"\nОбщая стоимость инвентаря: {factory.get_inventory_value():.2f} руб.")
