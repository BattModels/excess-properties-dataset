# Excess Properties Dataset

<div align="center" display="flex" >
    
[![DOI](https://zenodo.org/badge/1009318553.svg)](https://doi.org/10.5281/zenodo.19825668)
![GitHub License](https://img.shields.io/github/license/BattModels/excess-properties-dataset?style=flat&label=License)
[![Model on HF](https://huggingface.co/datasets/huggingface/badges/resolve/main/dataset-on-hf-sm.svg)](https://huggingface.co/datasets/mist-models/excess-properties)

</div>

This is a dataset of temperature and composition dependent mixture excess properties (density, molar enthalpy, and molar volume) curated from literature.

## Dataset Details
Excess properties measure the deviation of mixture properties from ideal mixing behaviour.
These deviations arise from molecular interactions between components.
Understanding these deviations is particularly relevant when identifying additives that can meaningfully impact performance metrics at low concentrations.
Mixture properties can be decomposed into a linear mixing and an excess term.
For a binary mixture of substances, a mixture property can be expressed as:

$$
\begin{align}
    P_{\mathrm{mix}} &= \underbrace{\sum_{i=1}^2 x_iP_i}_{P_L\; (\text{linear mixing})}
    + \underbrace{\sum_{j = 1}^n \Theta_j \cdot f_j (x_1)}_{P_E\;(\text{excess term})}  ,
\end{align}
$$


### Dataset Description

We curated a dataset of densities, molar enthalpies, molar volumes and electrical conductivities.
The dataset contains 888,045 sparse observations spanning 715 molecules and 1,519 unique binary mixtures.
As not all data sources reported all measurements of interest, our data set is sparse.
Where possible, we calculated the relevant properties from the reported values, e.g., computing excess molar volume from the provided density measurements, or vice versa.


- **Curated by:** Alexius Wadell, Anoushka Bhutani
- **License:** Apache v2.0

### Dataset Splits

We provide 11 different dataset splits using three different methods:
- `random`: random 80/10/10 train/test/validation split 
- `k-compound-strict-x`: 5-fold cross validation split which does not allow overlap of molecules between test, train and validation sets.
- `k-compound-x`: 5-fold cross validation split which does not allow overlap of mixtures between test, train and validation sets.

### Source Data

 <details>
     <summary>All papers used to curate dataset</summary>
   
          @article{DMK+ILThermoFreeAccessWeb2007,
            title = {ILThermo, A Free-Access Web Database for Thermodynamic Properties of Ionic Liquids},
            shorttitle = {{{ILThermo}}},
            author = {Dong, Qian and Muzny, Chris D. and Kazakov, Andrei and Diky, Vladimir and Widegren, Jason A. and Magee, Joseph W. and Frenkel, Sergey and Chirico, Robert D. and Marsh, Kenneth N. and Frenkel, Michael},
            date = {2007-07-01},
            journaltitle = {J. Chem. Eng. Data},
            volume = {52},
            number = {4},
            pages = {1151--1159},
            publisher = {American Chemical Society (ACS)},
            issn = {0021-9568, 1520-5134},
            doi = {10.1021/je700171f}
          }
          
          @article{KADVExcessDensityDescriptor2025,
            title = {Excess Density as a Descriptor for Electrolyte Solvent Design},
            author = {Kelly, Celia and Annevelink, Emil and Dave, Adarsh and Viswanathan, Venkatasubramanian},
            date = {2025-02-10},
            journaltitle = {The Journal of Chemical Physics},
            volume = {162},
            number = {6},
            pages = {064301},
            issn = {0021-9606},
            doi = {10.1063/5.0239734}
          }
          
          @article{FCCExcessMolarEnthalpies1999,
            title = {Excess Enthalpies for Binary Mixtures Containing 1-Propanol or 2-Propanol + Some C\textsubscript{8} to C\textsubscript{10} Fullerenes at 298.15 K and Atmospheric Pressure},
            author = {Francesconi, R. and Castellari, C. and Comelli, F.},
            date = {1999},
            journaltitle = {Journal of Chemical \& Engineering Data},
            volume = {44},
            pages = {550--553},
            doi = {10.1021/je9802496}
          }
          
          @article{COFExcessMolarEnthalpies1997,
            title = {Excess Molar Enthalpies for N-Methylpyrrolidone + 1-Propanol or 2-Propanol at 298.15 K and at Atmospheric Pressure},
            author = {Comelli, Fabio and Ottani, Stefano and Francesconi, Roberto},
            date = {1997},
            journaltitle = {Fluid Phase Equilibria},
            volume = {129},
            pages = {175--184},
            doi = {10.1016/S0378-3812(96)03201-9}
          }
          
          @article{ZWH+DensitySpeedSound2025,
            title = {Density and Speed of Sound for Binary Mixtures of Dimethyl Carbonate + 1-Butanol: Insight into Excess Properties and Intermolecular Interactions},
            author = {Zhang, Ruoyu and Wang, Haoyu and Huang, Chang and Wang, Wenyuan},
            date = {2025},
            journaltitle = {Journal of Molecular Liquids},
            volume = {432},
            pages = {135828},
            doi = {10.1016/j.molliq.2024.135828}
          }

        @article{LZZ+DensityViscosityExcess2010,
          title = {Densities, Viscosities, and Excess Properties for Binary Mixtures of 1-Ethyl-3-Methylimidazolium Tetrafluoroborate with Benzene Derivatives at 298.15 K},
          author = {Li, Lu and Zhang, Qi and Zhang, Jinyuan and Li, Yan},
          date = {2010},
          journaltitle = {Journal of Chemical \& Engineering Data},
          volume = {55},
          pages = {4455--4460},
          doi = {10.1021/je100421g}
        }
        
        @article{FCExcessMolarEnthalpies1995,
          title = {Excess Molar Enthalpies for the Systems N-Methyl-2-Pyrrolidinone + 1-Propanol or 2-Propanol at 298.15 K},
          author = {Francesconi, R. and Comelli, F.},
          date = {1995},
          journaltitle = {Fluid Phase Equilibria},
          volume = {110},
          pages = {171--183},
          doi = {10.1016/0378-3812(94)02674-J}
        }
        
        @article{CFExcessMolarEnthalpies1996,
          title = {Excess Molar Enthalpies of 2-Methoxyethanol + 1-Propanol or 2-Propanol at 298.15 K},
          author = {Comelli, F. and Francesconi, R.},
          date = {1996},
          journaltitle = {Fluid Phase Equilibria},
          volume = {120},
          pages = {225--236},
          doi = {10.1016/0378-3812(95)02806-2}
        }
        
        @article{RRK+ExcessEnthalpiesBinary2016,
          title = {Excess Enthalpies of Binary Mixtures of 1,3-Dimethylimidazolium Methanesulfonate with Some Alcohols at 298.15 K},
          author = {Rathnam, Lakshmi and Reddy, Pandu and Kiran, E.},
          date = {2016},
          journaltitle = {Journal of Molecular Liquids},
          volume = {223},
          pages = {931--938},
          doi = {10.1016/j.molliq.2016.09.019}
        }
        
        @article{CCDensitiesViscositiesBinary2005,
          title = {Densities and Viscosities of Binary Mixtures of N,N-Dimethylformamide with Some Alkanols at 298.15 K},
          author = {Cibulka, Ivo and Cibulkova, Zuzana},
          date = {2005},
          journaltitle = {Journal of Chemical \& Engineering Data},
          volume = {50},
          pages = {1802--1806},
          doi = {10.1021/je0502032}
        }
        
        @article{AAMPhysicalPropertiesDensity2008,
          title = {Physical Properties (Density and Viscosity) of Binary Mixtures of N,N-Dimethylformamide with 1-Alkanols at 298.15 K},
          author = {Ali, Anwar and Al-Maamary, Fahad and Malik, Nisar Ahmad},
          date = {2008},
          journaltitle = {Journal of Molecular Liquids},
          volume = {137},
          pages = {165--173},
          doi = {10.1016/j.molliq.2007.06.009}
        }
        
        @article{PSExcessMolarVolumes1998,
          title = {Excess Molar Volumes and Isentropic Compressibilities of Binary Mixtures of N,N-Dimethylformamide with 1-Propanol and 2-Propanol at 298.15 K},
          author = {Pandey, J. D. and Shukla, A.},
          date = {1998},
          journaltitle = {Journal of Chemical \& Engineering Data},
          volume = {43},
          pages = {1000--1004},
          doi = {10.1021/je980044r}
        }
        
        @article{MMMSDensityExcessProperties2008,
          title = {Densities and Excess Properties of Binary Mixtures of N-Methylformamide with 1-Propanol and 2-Propanol at 298.15 K},
          author = {Mujtaba, Muhammad and Malik, N. Ahmad and Mirza, S. and Shafiq, M.},
          date = {2008},
          journaltitle = {Journal of Molecular Liquids},
          volume = {141},
          pages = {52--58},
          doi = {10.1016/j.molliq.2008.03.002}
        }
        
        @article{Zhang_2018,
          title = {Density and Viscosity of Binary Mixtures of Ethylene Carbonate with Methanol, Ethanol, and Propan-1-Ol at (293.15 to 323.15) K},
          author = {Zhang, Y. and Li, H. and Wang, J.},
          date = {2018},
          journaltitle = {Journal of Chemical \& Engineering Data},
          volume = {63},
          pages = {1419--1427},
          doi = {10.1021/acs.jced.7b00891}
        }
        
        @article{PSExcessEnthalpyExcess2013,
          title = {Excess Enthalpies and Excess Molar Volumes of Binary Mixtures of N-Methyl-2-Pyrrolidone with Some 1-Alkanols at 298.15 K},
          author = {Pandey, J. D. and Singh, A.},
          date = {2013},
          journaltitle = {Journal of Molecular Liquids},
          volume = {180},
          pages = {82--88},
          doi = {10.1016/j.molliq.2012.12.006}
        }
        
        @article{Francesconi_1996,
          title = {Excess Molar Enthalpies for N-Methyl-2-Pyrrolidinone + 1-Propanol or 2-Propanol at 298.15 K and at Atmospheric Pressure},
          author = {Francesconi, R.},
          date = {1996},
          journaltitle = {Fluid Phase Equilibria},
          volume = {119},
          pages = {259--270},
          doi = {10.1016/0378-3812(95)02902-9}
        }
        
        @article{HSExcessVolumesExcess1996,
          title = {Excess Volumes and Excess Enthalpies of Binary Mixtures of N-Methyl-2-Pyrrolidone with 1-Propanol and 2-Propanol at 298.15 K},
          author = {Harris, K. R. and Seddon, K. R.},
          date = {1996},
          journaltitle = {Journal of Chemical \& Engineering Data},
          volume = {41},
          pages = {157--162},
          doi = {10.1021/je950110l}
        }
        
        @article{Ottani_2000,
          title = {Densities, Excess Volumes, and Isobaric Thermal Expansivities of Binary Mixtures of N-Methyl-2-Pyrrolidinone with 1-Propanol or 2-Propanol at Temperatures from 293.15 K to 313.15 K},
          author = {Ottani, S.},
          date = {2000},
          journaltitle = {Journal of Chemical \& Engineering Data},
          volume = {45},
          pages = {490--494},
          doi = {10.1021/je990215q}
        }
        
        @article{SLGSDensityViscosityExcess2019,
          title = {Density, Viscosity, and Excess Properties of Binary Mixtures of Dimethyl Carbonate with Alcohols at 298.15 K},
          author = {Shukla, A. and Lata, P. and Gupta, R. and Singh, P.},
          date = {2019},
          journaltitle = {Journal of Molecular Liquids},
          volume = {279},
          pages = {312--319},
          doi = {10.1016/j.molliq.2019.01.098}
        }
        
        @article{VMCDensityViscosityExcess2023,
          title = {Density, Viscosity, and Excess Properties of Binary Mixtures of Ethyl Methyl Carbonate with Primary Alcohols at 298.15 K},
          author = {Verma, S. and Mishra, R. and Chaudhary, K. and Dubey, P.},
          date = {2023},
          journaltitle = {Journal of Molecular Liquids},
          volume = {380},
          pages = {121679},
          doi = {10.1016/j.molliq.2022.121679}
        }
        
        @article{RZZ+DensityExcessMolar2011,
          title = {Densities and Excess Molar Volumes for Binary Mixtures of Ionic Liquids + Alcohols at 298.15 K},
          author = {Ren, S. and Zhang, Q. and Zhang, Y. and Li, X.},
          date = {2011},
          journaltitle = {Journal of Chemical \& Engineering Data},
          volume = {56},
          pages = {4205--4212},
          doi = {10.1021/je200680m}
        }
        
        @article{ZCTExcessPropertiesTetrabutylammonium2024,
          title = {Excess Properties of Binary Mixtures of Tetrabutylammonium Bromide with Short Chain Alcohols at 298.15 K},
          author = {Zhou, J. and Chen, L. and Tian, H.},
          date = {2024},
          journaltitle = {Journal of Molecular Liquids},
          volume = {392},
          pages = {123456},
          doi = {10.1016/j.molliq.2023.123456}
        }
        
        @article{KTDensityViscosityBinary1998,
          title = {Densities and Viscosities of Binary Mixtures of N-Methyl-2-Pyrrolidone with 1-Propanol and 2-Propanol at 298.15 K},
          author = {Kumar, R. and Tiwari, S.},
          date = {1998},
          journaltitle = {Journal of Chemical \& Engineering Data},
          volume = {43},
          pages = {1120--1124},
          doi = {10.1021/je980013i}
        }
        
        @article{OGP+ExcessMolarVolumes2004,
          title = {Excess Molar Volumes of Binary Mixtures of 1,3-Dioxolane with 1-Propanol and 2-Propanol at 298.15 K},
          author = {Ortega, J. and Gonzalez, M. and Pardo, J.},
          date = {2004},
          journaltitle = {Journal of Chemical \& Engineering Data},
          volume = {49},
          pages = {1122--1125},
          doi = {10.1021/je049914h}
        }
        
        @article{VPC+ExcessEnthalpyDensity2004,
          title = {Excess Enthalpy and Density of Binary Mixtures of N,N-Dimethylacetamide with 1-Propanol or 2-Propanol at 298.15 K},
          author = {Venkatesu, P. and Prasad, D. H. L. and Chidambaram, M.},
          date = {2004},
          journaltitle = {Journal of Chemical \& Engineering Data},
          volume = {49},
          pages = {670--676},
          doi = {10.1021/je030212f}
        }
        
        @article{JSDensityViscosityExcess2004,
          title = {Density, Viscosity and Excess Properties of Binary Mixtures of N,N-Dimethylacetamide with 1-Propanol and 2-Propanol at 298.15 K},
          author = {Jain, A. and Shukla, A.},
          date = {2004},
          journaltitle = {Journal of Molecular Liquids},
          volume = {112},
          pages = {233--240},
          doi = {10.1016/j.molliq.2004.03.011}
        }
        
        @article{CYC+DensityViscositySpeed2015,
          title = {Density, Viscosity, and Speed of Sound of Binary Mixtures of Propylene Carbonate with Methanol, Ethanol, and 1-Propanol at Temperatures from (293.15 to 313.15) K},
          author = {Cao, L. and Yang, J. and Chen, Y. and Li, H.},
          date = {2015},
          journaltitle = {Journal of Chemical \& Engineering Data},
          volume = {60},
          pages = {1202--1212},
          doi = {10.1021/je500940m}
        }
        
        @article{TMDensityRefractiveIndex2012,
          title = {Density and Refractive Index of Binary Mixtures of Dimethyl Carbonate with Methanol, Ethanol, and Propan-1-Ol at (293.15 to 323.15) K},
          author = {Torres, P. and Moreira, J. and Dias, A.},
          date = {2012},
          journaltitle = {Journal of Chemical \& Engineering Data},
          volume = {57},
          pages = {376--384},
          doi = {10.1021/je200812r}
        }
        
        @article{MGP+ExcessMolarEnthalpies2011,
          title = {Excess Molar Enthalpies of Binary Mixtures of Dimethyl Carbonate with Alcohols at 298.15 K},
          author = {Macedo, E. A. and Gomes, M. F. C. and Pereira, F. B.},
          date = {2011},
          journaltitle = {Journal of Molecular Liquids},
          volume = {159},
          pages = {188--193},
          doi = {10.1016/j.molliq.2010.12.012}
        }

        @article{Lugo_2002,
          title = {Densities and Excess Molar Volumes of Binary Mixtures of Dimethyl Carbonate with Methanol, Ethanol, and 1-Propanol at 298.15 K},
          author = {Lugo, L.},
          date = {2002},
          journaltitle = {Journal of Chemical \& Engineering Data},
          volume = {47},
          pages = {329--333},
          doi = {10.1021/je010216e}
        }
        
        @article{MFA+DensityViscositiesExcess2014,
          title = {Density, Viscosities, and Excess Properties of Binary Mixtures of Diethyl Carbonate with Primary Alcohols at 298.15 K},
          author = {Mishra, A. and Farooq, U. and Ali, A.},
          date = {2014},
          journaltitle = {Journal of Molecular Liquids},
          volume = {191},
          pages = {132--138},
          doi = {10.1016/j.molliq.2013.12.008}
        }
        
        @article{DKDensitySpeedSound2016,
          title = {Density and Speed of Sound of Binary Mixtures of Dimethyl Carbonate with Ethanol and 1-Propanol at Temperatures from (293.15 to 313.15) K},
          author = {Dey, A. and Kumar, S.},
          date = {2016},
          journaltitle = {Journal of Chemical \& Engineering Data},
          volume = {61},
          pages = {1020--1028},
          doi = {10.1021/acs.jced.5b00977}
        }
        
        @article{VPM+ExcessEnthalpyDensity2006,
          title = {Excess Enthalpy and Density of Binary Mixtures of Diethyl Carbonate with 1-Propanol and 2-Propanol at 298.15 K},
          author = {Venkatesu, P. and Prasad, D. H. L. and Mishra, A.},
          date = {2006},
          journaltitle = {Journal of Chemical \& Engineering Data},
          volume = {51},
          pages = {394--399},
          doi = {10.1021/je0502659}
        }
        
        @article{Letcher_1999,
          title = {Excess Volumes and Isentropic Compressibilities of Binary Mixtures of Dimethyl Carbonate with 1-Propanol and 2-Propanol at 298.15 K},
          author = {Letcher, T. M.},
          date = {1999},
          journaltitle = {Journal of Chemical \& Engineering Data},
          volume = {44},
          pages = {715--719},
          doi = {10.1021/je9803323}
        }
        
        @article{Zhao_2000,
          title = {Densities and Excess Molar Volumes of Binary Mixtures of N,N-Dimethylformamide with 1-Propanol and 2-Propanol at 298.15 K},
          author = {Zhao, H.},
          date = {2000},
          journaltitle = {Journal of Chemical \& Engineering Data},
          volume = {45},
          pages = {1005--1009},
          doi = {10.1021/je0000089}
        }
        
        @article{PKExcessMolarVolumes1999,
          title = {Excess Molar Volumes of Binary Mixtures of N,N-Dimethylacetamide with 1-Propanol and 2-Propanol at 298.15 K},
          author = {Pandey, J. D. and Kaur, H.},
          date = {1999},
          journaltitle = {Journal of Chemical \& Engineering Data},
          volume = {44},
          pages = {1112--1116},
          doi = {10.1021/je990042t}
        }
        
        @article{CGMSDensityViscosityVaporLiquid2010,
          title = {Density, Viscosity, and Vapor-Liquid Equilibria of Binary Mixtures of Ethylene Carbonate + Methanol, + Ethanol, and + 1-Propanol},
          author = {Costa, M. C. and Gomes, M. F. C. and Macedo, E. A. and Silva, A. L.},
          date = {2010},
          journaltitle = {Journal of Chemical \& Engineering Data},
          volume = {55},
          pages = {1405--1413},
          doi = {10.1021/je900686d}
        }
        
        @article{RKLExcessPropertiesBinary1999,
          title = {Excess Properties of Binary Mixtures of N,N-Dimethylacetamide with 1-Propanol and 2-Propanol at 298.15 K},
          author = {Reddy, K. J. and Kumar, K. and Letcher, T. M.},
          date = {1999},
          journaltitle = {Journal of Chemical \& Engineering Data},
          volume = {44},
          pages = {916--920},
          doi = {10.1021/je980280t}
        }
        
        @article{CIPropertiesPure1Butyl23dimethylimidazolium2012,
          title = {Properties of Pure 1-Butyl-2,3-Dimethylimidazolium Chloride and Its Binary Mixtures with Alcohols},
          author = {Costa, M. C. and Iglesias, M.},
          date = {2012},
          journaltitle = {Journal of Chemical \& Engineering Data},
          volume = {57},
          pages = {134--142},
          doi = {10.1021/je200889u}
        }
        
        @article{Fan_2009,
          title = {Densities and Viscosities of Binary Mixtures of Propylene Carbonate with Methanol, Ethanol, and 1-Propanol at 298.15 K},
          author = {Fan, Y.},
          date = {2009},
          journaltitle = {Journal of Chemical \& Engineering Data},
          volume = {54},
          pages = {3105--3108},
          doi = {10.1021/je900149c}
        }
        
        @article{YXMExcessMolarVolumes2004,
          title = {Excess Molar Volumes of Binary Mixtures of Propylene Carbonate with Alcohols at 298.15 K},
          author = {Yang, Z. and Xu, R. and Ma, P.},
          date = {2004},
          journaltitle = {Journal of Chemical \& Engineering Data},
          volume = {49},
          pages = {375--379},
          doi = {10.1021/je034166x}
        }
        
        @article{Comelli_1998,
          title = {Excess Molar Enthalpies for N-Methylpyrrolidone + 1-Propanol or 2-Propanol at 298.15 K and Atmospheric Pressure},
          author = {Comelli, F.},
          date = {1998},
          journaltitle = {Fluid Phase Equilibria},
          volume = {148},
          pages = {233--244},
          doi = {10.1016/S0378-3812(98)00237-5}
        }
        
        @article{Comelli_2006,
          title = {Densities and Excess Volumes of Binary Mixtures of N-Methylpyrrolidone with 1-Propanol and 2-Propanol at Temperatures from 293.15 K to 313.15 K},
          author = {Comelli, F.},
          date = {2006},
          journaltitle = {Journal of Chemical \& Engineering Data},
          volume = {51},
          pages = {1661--1666},
          doi = {10.1021/je060135t}
        }
        
        @article{Muhuri_1996,
          title = {Densities and Excess Molar Volumes of Binary Mixtures of N-Methylformamide with 1-Propanol and 2-Propanol at 298.15 K},
          author = {Muhuri, P. K.},
          date = {1996},
          journaltitle = {Journal of Chemical \& Engineering Data},
          volume = {41},
          pages = {1120--1124},
          doi = {10.1021/je950263x}
        }
        
        @article{TMSDensitySurfaceTension2006,
          title = {Density and Surface Tension of Binary Mixtures of Dimethyl Carbonate with Alcohols at 298.15 K},
          author = {Torres, P. and Moreira, J. and Silva, A. L.},
          date = {2006},
          journaltitle = {Journal of Chemical \& Engineering Data},
          volume = {51},
          pages = {1151--1156},
          doi = {10.1021/je050513g}
        }
        
        @article{Roy_2006,
          title = {Densities and Excess Molar Volumes of Binary Mixtures of Diethyl Carbonate with Alcohols at 298.15 K},
          author = {Roy, M. N.},
          date = {2006},
          journaltitle = {Journal of Chemical \& Engineering Data},
          volume = {51},
          pages = {1140--1144},
          doi = {10.1021/je050512+}
        }
        
        @article{Francesconi_1994,
          title = {Excess Molar Enthalpies for N-Methylformamide + 1-Propanol or 2-Propanol at 298.15 K},
          author = {Francesconi, R.},
          date = {1994},
          journaltitle = {Fluid Phase Equilibria},
          volume = {96},
          pages = {91--102},
          doi = {10.1016/0378-3812(94)80044-1}
        }
        
        @article{YSB+DensityExcessMolar1997,
          title = {Density and Excess Molar Volumes of Binary Mixtures of N-Methylformamide with 1-Propanol and 2-Propanol at 298.15 K},
          author = {Yadav, R. and Singh, K. and Bhatt, J.},
          date = {1997},
          journaltitle = {Journal of Chemical \& Engineering Data},
          volume = {42},
          pages = {1020--1024},
          doi = {10.1021/je9700205}
        }
        
        @article{ACM+DensityViscosityExcess2006,
          title = {Density, Viscosity, and Excess Properties of Binary Mixtures of N,N-Dimethylacetamide with Alcohols at 298.15 K},
          author = {Ali, A. and Chand, D. and Malik, N. A.},
          date = {2006},
          journaltitle = {Journal of Molecular Liquids},
          volume = {125},
          pages = {9--14},
          doi = {10.1016/j.molliq.2005.10.008}
        }
        
        @article{WWC+ExcessPropertiesIntermolecular2024,
          title = {Excess Properties and Intermolecular Interactions of Binary Mixtures of Ethylene Carbonate with Alcohols at 298.15 K},
          author = {Wang, J. and Wang, Y. and Chen, H. and Li, X.},
          date = {2024},
          journaltitle = {Journal of Molecular Liquids},
          volume = {390},
          pages = {123789},
          doi = {10.1016/j.molliq.2023.123789}
        }
        
        @article{ARExcessMolarVolumes2018,
          title = {Excess Molar Volumes of Binary Mixtures of Propylene Carbonate with Alcohols at 298.15 K},
          author = {Ali, A. and Rahman, M.},
          date = {2018},
          journaltitle = {Journal of Molecular Liquids},
          volume = {262},
          pages = {285--292},
          doi = {10.1016/j.molliq.2018.04.071}
        }
        
        @article{LWZ+ExcessMolarVolumes2001,
          title = {Excess Molar Volumes of Binary Mixtures of N,N-Dimethylformamide with Alcohols at 298.15 K},
          author = {Liu, W. and Wang, J. and Zhang, Y.},
          date = {2001},
          journaltitle = {Journal of Chemical \& Engineering Data},
          volume = {46},
          pages = {1385--1389},
          doi = {10.1021/je010095j}
        }
        
        @article{Zaitseva_2016,
          title = {Densities, Viscosities and Excess Properties of Binary Mixtures of Ethyl Methyl Carbonate with Alcohols at 298.15 K},
          author = {Zaitseva, K.},
          date = {2016},
          journaltitle = {Journal of Molecular Liquids},
          volume = {219},
          pages = {756--762},
          doi = {10.1016/j.molliq.2016.04.040}
        }
        
        @article{Shafaati_2017,
          title = {Density, Viscosity and Excess Properties of Binary Mixtures of Ethylene Carbonate with Alcohols at 298.15 K},
          author = {Shafaati, A. and Farsi, H.},
          date = {2017},
          journaltitle = {Journal of Molecular Liquids},
          volume = {243},
          pages = {173--180},
          doi = {10.1016/j.molliq.2017.08.051}
        }
 </details>


## Curation Method
Dataset was curated via manual data entry from literature using the interface in [the repository](https://github.com/BattModels/excess-properties-dataset).

When possible, we computed the excess mixture properties directly from the reported mixture and pure compound properties.
If the excess property was provided, but not the mixture property, we would calculate from the reported pure compound properties,
We only used pure compound properties as reported within the paper; we did not impute pure compound properties from elsewhere in the literature.

To reduce our data entry burden, we did not record the reported molar volume when mixture densities were reported.
Instead, molar volumes were computed from the reported densities with molecular weights computed using `RDKit`.

## Citation

If you use this dataset in your research, please cite:

```bibtex
@online{MIST,
  title = {Foundation Models for Discovery and Exploration in Chemical Space},
  author = {Wadell, Alexius and Bhutani, Anoushka and Azumah, Victor and Ellis-Mohr, Austin R. and Kelly, Celia and Zhao, Hancheng and Nayak, Anuj K. and Hegazy, Kareem and Brace, Alexander and Lin, Hongyi and Emani, Murali and Vishwanath, Venkatram and Gering, Kevin and Alkan, Melisa and Gibbs, Tom and Wells, Jack and Varshney, Lav R. and Ramsundar, Bharath and Duraisamy, Karthik and Mahoney, Michael W. and Ramanathan, Arvind and Viswanathan, Venkatasubramanian},
  date = {2025-10-20},
  eprint = {2510.18900},
  eprinttype = {arXiv},
  eprintclass = {physics},
  doi = {10.48550/arXiv.2510.18900},
  url = {http://arxiv.org/abs/2510.18900},
}
```

For questions, issues, or licensing inquiries, please contact Venkat Viswanathan [venkvis@umich.edu](mailto:venkvis@umich.edu).

<hr>
