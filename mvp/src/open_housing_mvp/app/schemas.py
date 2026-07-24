"""Schémas Pydantic de l'API MVP (US-13)."""

from pydantic import BaseModel, ConfigDict, Field


class HouseFeatures(BaseModel):
    crim: float = Field(..., description="Taux de criminalité par habitant")
    zn: float = Field(..., description="Proportion de terrain résidentiel zoné grandes parcelles")
    indus: float = Field(..., description="Proportion d'acres commerciaux non liés au détail")
    chas: int = Field(..., ge=0, le=1, description="Bordure de la rivière Charles (1) ou non (0)")
    nox: float = Field(..., description="Concentration en oxydes d'azote")
    rm: float = Field(..., gt=0, description="Nombre moyen de pièces par logement")
    age: float = Field(..., ge=0, description="Proportion de logements occupés construits avant 1940")
    dis: float = Field(..., gt=0, description="Distance pondérée aux centres d'emploi")
    rad: float = Field(..., description="Indice d'accessibilité aux autoroutes radiales")
    tax: float = Field(..., description="Taux de taxe foncière")
    ptratio: float = Field(..., description="Ratio élèves/enseignant")
    b: float = Field(
        ...,
        description=(
            "Variable socio-démographique du dataset d'origine — limite éthique connue, "
            "non arbitrée avec le business (voir BACKLOG_PRODUIT_v2.md)"
        ),
    )
    lstat: float = Field(..., description="Pourcentage de population à statut socio-économique inférieur")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "crim": 0.00632, "zn": 18.0, "indus": 2.31, "chas": 0, "nox": 0.538,
                "rm": 6.575, "age": 65.2, "dis": 4.09, "rad": 1, "tax": 296,
                "ptratio": 15.3, "b": 396.9, "lstat": 4.98,
            }
        }
    )


class PredictionResponse(BaseModel):
    predicted_price: float


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
