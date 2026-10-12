# Three-dimensional thermal characterization of forest canopies using UAV photogrammetry

![image](https://cdn-mineru.openxlab.org.cn/result/2026-09-22/88455dc8-52f5-45be-aa4a-0962988e173b/7f186a5d8ee3151e6086a7ccc3caf4ff6aaea9f07aa932033e8562ac81836c0a.jpg)


Clare Webster<sup>a,b,⁎</sup>, Matthew Westoby<sup>a</sup>, Nick Rutter<sup>a</sup>, Tobias Jonas<sup>b</sup> 

<sup>a</sup> Department of Geography, Northumbria University, Newcastle upon Tyne, UK <sup>b</sup> WSL Institute for Snow and Avalanche Research SLF, Davos, Switzerland 

## A R T I C L E I N F O

Keywords: Thermal infrared imagery Structure from motion Digital photogrammetry Computer vision Canopy structure Forest structure Forest monitoring Unmanned aerial vehicle Unmanned aerial system UAV UAS Forest canopy temperature Temperature heterogeneity 

## A B S T R A C T

Measurements of vegetation structure have become a valuable tool for ecological research and environmental management. However, data describing the thermal 3D structure of canopies and how they vary both spatially and temporally remain sparse. Coincident RGB and thermal imagery from a UAV platform were collected of both a standalone tree and a relatively dense forest stand in the sub-alpine Eastern Swiss Alps. For the <sup>fi</sup>rst time, SfM MVS methods were used to develop 3D RGB and thermal point clouds of the two sites with point densities of 35,245 and 776 points per m<sup>2</sup>, respectively, compared to 78 points per m<sup>2</sup> for an airborne LiDAR dataset of the same area. Despite the low resolution of the thermal imagery compared to RGB photosets, forest structural elements were accurately resolved in both point clouds. Improvements in the quality of the thermal 3D data were gained through the application of a distance <sup>fi</sup>lter based on the proximity of these data to the RGB 3D point data. Vertical temperature gradients of trees were negative with increasing height at the standalone tree. but were positive in the dense stand largely due to increased self-shading of incoming shortwave energy. Repeat surveys across a single morning during the snowmelt period revealed changes in the spatial distribution of canopy temperatures which are consistent with canopy warming from direct solar radiation. This is the <sup>fi</sup>rst time tha coincidentally acquired RGB and thermal imagery have been combined to generate separate RGB and thermal point clouds of 3D structures. These methods and <sup>fi</sup>ndings demonstrate important implications for atmospheric, hydrological and ecological modeling, and have wide application for e<sup>f</sup>ective thermal measurements of remote environmental landscapes. 

## 1. Introduction

Forests cover approximately 31% of the total global surface area (FAO, 2010), regulating local and global energy balance and biogeochemical cycles, providing wildlife habitat and supporting biodiversity. Understanding, management and prediction of forest processes depends greatly on measurement of forested environments (e.g. structure, biomass, temperature, habitat quality and biodiversity) at su<sup>fi</sup>cient spatial and temporal resolution. To this end, three-dimensional (3D) mapping of forest canopies has become a valuable tool for obtaining forest canopy structure information, such as e<sup>f</sup>ective leaf area index, fractional cover and canopy closure (Morsdorf et al., 2006: Solberg et al., 2009). These forest canopy structure parameters have been applied to carbon accounting (Houghton et al., 2009; Kobayashi et al., 2012), canopy structure modeling for ecosystem analysis (Zhao and Popescu, 2009), energy balance (Musselman et al., 2013) and radiative transfer modeling (Essery et al., 2008a), as well as search and rescue logistics (Rudol and Doherty, 2008). 

Remotely sensed data describing 3D forest structures have been retrieved using airborne or terrestrial light detection and ranging methods (LiDAR; Kankare et al., 2013; Liang et al., 2012; Lucas et al., 2008; Srinivasan et al., 2014; Wagner et al., 2008). LiDAR data can be acquired across large (> 50,000 ha) areas in a series of repeat over-<sup>fl</sup>ights. However, the commission of LiDAR <sup>fl</sup>ights or data purchase can exceed USD$20,000 per <sup>fl</sup>ight (Erdody and Moskal, 2010), particularly when data at high spatial and temporal resolutions are required. More recently, improvements in the a<sup>f</sup>ordability and accessibility of lightweight unmanned aerial vehicle (UAV, or ‘drone’) technology has facilitated low-cost methods of low-altitude (< 150 m <sup>fl</sup>ying height) photographic and videographic data collection in a range of environments (e.g. Cohen et al., 2005; Dandois and Ellis, 2013; Faye et al., 2016; Morgenroth and Gomez, 2014). The deployment of lightweight <sup>fi</sup>xed-wing or multi-rotor UAV systems with on-board digital imaging sensors facilitates the collection of remotely sensed data at increasingly high spatial and temporal resolutions. Further advances in the development of <sup>fl</sup>ight planning software now facilitate GPS-guided <sup>fl</sup>ight 

![image](https://cdn-mineru.openxlab.org.cn/result/2026-09-22/88455dc8-52f5-45be-aa4a-0962988e173b/850f245898e57c12c68278c4c85f297e809a4b7b5183ccbe1f8230822c457e4c.jpg)


![image](https://cdn-mineru.openxlab.org.cn/result/2026-09-22/88455dc8-52f5-45be-aa4a-0962988e173b/28bce811eb90f9a982671cb6f954347fdb0414e6245df05375310b79774936cb.jpg)


![image](https://cdn-mineru.openxlab.org.cn/result/2026-09-22/88455dc8-52f5-45be-aa4a-0962988e173b/46fa72971b9a70419da5f584cc2b5c67c665a8cdd42f1697112c2769e2a58a7d.jpg)


![image](https://cdn-mineru.openxlab.org.cn/result/2026-09-22/88455dc8-52f5-45be-aa4a-0962988e173b/0c5850ce40e0a84fbb8fb8d96d5eae60b9c9ed9c410d8eaef27f7122cc025768.jpg)



Aerial images and background images from © CNES, Spot Image, reproduced with permission from Swisstopo, NPOC (JA100118).



Fig. 1. Overview of the two <sup>fi</sup>eld locations, showing a. relative location between the tree in Dischma Valley and the forest <sup>fi</sup>eld site in Laret; b. aerial image of single tree in Dischma Valley; c. aerial image and outline of <sup>fl</sup>ight area over the forest <sup>fi</sup>eld site in Laret; d. airborne LiDAR point-cloud data of forest <sup>fi</sup>eld site in Laret showing canopy distribution and surface height.


repeatability. 

The recent emergence of a new generation of digital photogrammetric and computer vision-based algorithms for reconstructing 3D scene topography from 2D input imagery, popularly known as ‘Structure-from-Motion’ (SfM) has revolutionized the field of 3D data acquisition and analysis (e.g. Carrivick et al., 2016; James and Robson, 2012; Snavely et al., 2008; Westoby et al., 2012), and originates from advances in the computer vision community (e.g. Spetsakis and Aloimonos, 1991; Boufama et al., 1993; Szeliski and Kang, 1994). Unlike conventional photogrammetric techniques, SfM methods identify matching features in overlapping digital images and use this information as input to an iterative bundle adjustment which simultaneously solves for the interior and exterior camera parameters and generates a sparse 3D point-cloud. This process can be enhanced through the use of input imagery which has been geotagged using GPS technology. SfM algorithms are commonly used in conjunction with multi-view stereo methods (SfM-MVS) to increase 3D point densities, typically by an order of magnitude or more (Carrivick et al., 2016; James and Robson, 2012; Westoby et al., 2012), whilst the addition of ground control points (GCP) with known xyz positions in the scene facilitates the georegistration of SfM-derived 3D data. 

A number of recent studies have employed SfM-MVS methods to derive 3D models of forest canopy structure from RGB imagery acquired from UAVs (e.g. Dandois and Ellis, 2010; Dandois and Ellis, 2013; Mlambo et al., 2017). Example applications of SfM-MVS for vegetation analysis include the use of color channel segmentation to facilitate species identi<sup>fi</sup>cation and the analysis of plant stress and seasonal development (Dandois and Ellis, 2013), and the estimation of aboveground biomass volumes (Bendig et al., 2014). Signi<sup>fi</sup>cantly, Dandois and Ellis (2013) found that tree heights extracted from SfM-MVS-derived point-clouds correlated well with equivalent data extracted from airborne LiDAR $( \mathrm { R } ^ { 2 } = 0 . 8 7 )$ and <sup>fi</sup>eld measurements $( \mathrm { R } ^ { 2 } = 0 . 6 3 – 0 . 8 4 ) _ { ; }$ whilst additional studies have also found the accuracy of SfM-MVSderived datasets to closely mirror those obtained using terrestrial or airborne LiDAR (Hernández-Clemente et al., 2014; Wallace et al., 2016). Furthermore, Faye et al. (2016) have demonstrated a work<sup>fl</sup>ow for simultaneous, two-dimensional (2D) thermal infrared (TIR) and RGB airborne imaging in ecological monitoring. Whilst these studies have demonstrated signi<sup>fi</sup>cant advances in the remote sensing of vegetation structure, the integration of thermal information into 3D forest canopy structure models has to date received limited attention. 

Measurements of forest canopy temperature at a range of spatial scales can provide insights into energy <sup>fl</sup>ux (Webster et al., 2016), evapotranspiration and photosynthesis (Solberg et al., 2009), and plant stress (Erdody and Moskal, 2010; Morsdorf et al., 2006). Forest canopy temperature is therefore an important parameter in environmental monitoring and modeling. Thermal imaging technology has advanced to the stage where survey grade, portable, and easy to use cameras are readily available and relatively a<sup>f</sup>ordable (< USD$12,000). This in creasing availability has allowed for diverse applications of TIR imagery in remote environments for a number of environmental monitoring and modeling applications, including water management and agriculture (Anderson et al., 2012; Berni et al., 2009; Gago et al., 2015; Leinonen et al., 2006), visualization of lava <sup>fl</sup>ow evolution (James et al., 2009), volcanic activity (Spampinato et al., 2011), and ground water movement (Luscombe et al., 2015; P<sup>fi</sup>ster et al., 2010). Studies employing airborne thermal imagery have generally utilized 2D imaging outputs, however, the processing of 2D thermal imagery to produce fully 3D models containing thermal information has yet to be fully explored in the context of forest canopy structure. Signi<sup>fi</sup>cantly, to date no single instrument or imaging system has been demonstrated to have the capacity for retrieving both structural and thermal observa tions of forest canopies in 3D and at high spatial and temporal resolu tions. 

This paper appraises the capacity of SfM-MVS methods for retrieving structural and thermal 3D data of vegetation structures using coincident RGB and thermal imagery acquired from a UAV. We <sup>fi</sup>rst present and discuss the acquisition, generation, and analysis of 3D RGB and thermal data for a single, standalone tree, before demonstrating and discussing the utility of our work<sup>fl</sup>ow for characterizing the structure and thermal signature of a heterogeneous alpine forested area during the northern hemisphere snowmelt season. 

## 2. Study sites

Two sub-alpine forest study sites near the town of Davos, Switzerland were selected for analysis (Fig. 1a). The <sup>fi</sup>rst site is a standalone Norway Spruce (Picea abies) tree located in the Dischma valley (46.757°N, 9.879°E; Fig. 1b). The tree is ~18 m high, and has a diameter of 8 m. The second site is a relatively dense forest stand of predominantly Norway Spruce $( \sim 3 0 \mathrm { m } \times 3 0 \mathrm { m } )$ close to Davos Laret, Switzerland (46.843°N, 9.875°E; Fig. 1c, d). Tree heights in this area range between 12 and 40 m. 

The use of single-species forested environments for thermal imaging is largely straightforward compared to other land surfaces as emissivity is typically strongly homogeneous (Price and Petzold, 1984). Flights over land surfaces with a variable surface emissivity, such as agricultural cropland, would require a further step in post-processing to ensure accurate surface temperatures are calculated (e.g. Faye et al., 2016). Additionally, the collection of data across the forest stand during winter when seasonal snow was present on the ground surface allowed strong thermal contrast between the canopy and the forest <sup>fl</sup>oor, creating an obvious mask between the two features. 

## 3. Methods and data products

## 3.1. UAV platform and sensors

UAV <sup>fl</sup>ights were undertaken with a DJI S1000 octocopter (Fig. 2a). RGB imagery was acquired using a Panasonic Lumix DMC-GH4 digital SLR camera (Fig. 2b) at an original resolution of 4608 × 2592 pixels (1:0.57 scaling) and with manual exposure and focusing settings enabled. The camera was triggered using an intervalometer, set at a 1- second interval. Thermal imagery was acquired in the form of raw .csv <sup>fi</sup>les using an Optris PI450 Thermal Imager, controlled using an onboard NetBox running a Windows XP Professional operating system and PI Connect software (Fig. 2b). The NetBox is a miniature PC attached to the camera that allows the IR camera to operate as a stand-alone unit. This permits longer distances between the camera and the monitoring system (traditional PC), allowing it to functionally operate on remote systems such as the UAV in this study. The PI450 thermal imager has a resolution of 382 × 288 pixels and obtains thermal data in the spectral range 7.5–13 μm. The imager is self-calibrating and has a manufacturerstated measurement accuracy $0 \mathrm { f } \pm 2 \% 0 \mathrm { r } \pm 2 \mathrm {  { \tau } C }$ and provides a raw output in °C. The emissivity of the scene was set to 1 for all thermal imagery, which were acquired at 1-second intervals. The use of an emissivity of 1 assumes there is zero re<sup>fl</sup>ectance from the canopy. The maximum image timing o<sup>f</sup>set between sequential RGB and thermal images is < 2 s. A summary of the instrumentation speci<sup>fi</sup>cations is provided in Table 1. 

The two sensors were mounted underneath the UAV using a custom bracket attached to a motorized, gyroscopically stabilized gimbal in a con<sup>fi</sup>guration which dampens vibrations and helps to maintains sensor stability in the xy plane when the sensors are positioned in a downward-facing (nadir) perspective (Fig. 2b). This con<sup>fi</sup>guration also ensured a general correspondence between RGB and thermal image centers at operational <sup>fl</sup>ying heights, whilst the ground footprint of each sensor varied slightly as a function of sensor resolution and radial distortion e<sup>f</sup>ects. Including batteries, the UAV and multi-sensor imaging system weighed ~12 kg. The UAV included an on-board navigation system, including integrated Global Navigation Satellite Systems (GNSS), Inertial Measurement Unit (IMU) and barometer and compass components, which facilitate high positional accuracy and UAV stabilization in winds up to 28 km/h and in temperatures of > –5°C. 

## 3.2. Data acquisition

Flight missions over the single standalone tree at the Dischma test site (Fig. 1b) were manually controlled and assisted by an on-board <sup>fi</sup>rst-person-view (FPV) camera, connected to a monitor via a 5.8GHz connection. Flight elevation was maintained at 25 $\mathbf { m } , < 1 0$ m above the top of the tree and the thermal camera was focused at approximately 15 m distance with a depth of <sup>fi</sup>eld of approximately 5.3 m. A <sup>fl</sup>ying speed of $1 \mathrm { m } s ^ { - 1 }$ was maintained throughout the <sup>fl</sup>ight, which was < 5 min in duration due to the small spatial coverage required. The ground was completely snow-free during data acquisition at the Dischma site. 

Flight missions for the forest stand at the Laret test site were planned using DJI PC Ground Station software (v. 4.0.11.) installed on a portable <sup>fi</sup>eld laptop computer with a 2.4 GHz wireless data link, allowing continuous radio communication for real-time <sup>fl</sup>ight monitoring and intervention. Flight plans were programmed in a predetermined square-parallel sweep pattern using a constant <sup>fl</sup>ying height of 50 m (< 10 m above the canopy) and a forward <sup>fl</sup>ight speed of $1 \mathrm { m } s ^ { - 1 }$ corresponding to forward and side image overlap of 80% and 40%. Transects were 18.5 m long and spaced 5.8 m apart. The thermal camera was manually focused at approximately 25 m distance with a depth of <sup>fi</sup>eld of approximately 7.6 m. Maximum <sup>fl</sup>ight time was < 10 min using a 16,000 mAh battery, which was su<sup>fi</sup>cient to survey the entire <sup>fi</sup>eld site in a single <sup>fl</sup>ight. 

Speci<sup>fi</sup>c meteorological and canopy conditions were required for collection of airborne thermal imagery. Flights across the forest stand during winter were carried out when there was no intercepted snow on the canopy in order to allow full thermal visualization of a snow-free canopy surface. The ground was completely snow covered with no bare ground in the sub-canopy. Additionally, this removed possible error in 3D reconstruction arising from snow present in the canopy and on the ground having the same spectral characteristics in the RGB and thermal images. Meteorological conditions (incoming shortwave radiation, air temperature) were recorded at a weather station installed in a local open site approximately 300 m to the northwest of the forest <sup>fl</sup>ight area and 2 km northwest of the Dischma single tree site. 

E<sup>f</sup>ects on image accuracy arising from surface roughness, air tem perature changes and humidity were to be negligible due to the proximity of the canopy to the camera (< 10 m). Corrections for atmospheric in<sup>fl</sup>uences on thermal imaging accuracy were not required as these e<sup>f</sup>ects in<sup>fl</sup>uence temperature accuracy when the target is > 100 m from the imager (Ball and Pinkerton, 2006). 

A network of ground control points (GCPs) was established prior to UAV deployment at each <sup>fi</sup>eld site, and their xyz location surveyed using a Leica TPS 1200 total station and Trimble GR5 RTK di<sup>f</sup>erential GPS. GCPs measured $0 . 8 \times 0 . 5 \mathrm { m }$ and consisted of a material with a relatively large re<sup>fl</sup>ectance in the IR domain with a border of adhesive black plastic (Fig. 2c). These materials were chosen due to their contrasting emissivity, which produced a clear boundary between the two materials and the ground when viewed in a thermal image (Fig. 2d). GCPs were equally visible in the corresponding RGB imagery. At the single tree, twelve GCPs were arranged in concentric inner and outer circles around the standalone tree. At the forest stand, the twelve GCPs were positioned across the forest area in a quasi-uniform grid pattern in small gaps between the trees in order to maximize their visibility during aerial surveying. Snow height was measured below the GCPs in the forest stand site and each z location was corrected in post-processing to correspond to ground height. 


Table 1


![image](https://cdn-mineru.openxlab.org.cn/result/2026-09-22/88455dc8-52f5-45be-aa4a-0962988e173b/b2406f8d08c7be33b23fc00516aed76779a6107729881218ce41791ee7cb4e31.jpg)


![image](https://cdn-mineru.openxlab.org.cn/result/2026-09-22/88455dc8-52f5-45be-aa4a-0962988e173b/6f9fe9a96bfdcf07b6ab6a25ab840047274429388910beac1f6a98bab401889a.jpg)


![image](https://cdn-mineru.openxlab.org.cn/result/2026-09-22/88455dc8-52f5-45be-aa4a-0962988e173b/5b981c881caa5f994e4b779d8057fd65df02b456ddcdc45f41532d9c2ba08e65.jpg)


![image](https://cdn-mineru.openxlab.org.cn/result/2026-09-22/88455dc8-52f5-45be-aa4a-0962988e173b/fb06ed29a907dc7f67b66115733504e85c2a027ae7317964fffd75fc8e0c49a9.jpg)



Fig. 2. a. DJI S1000 Octocopter in <sup>fl</sup>ight <sup>fi</sup>tted with; b. gimbal with Optris PI450 imager (I), NetBox (II) and Panasonic Lumix RGB camera (III); c. example of thermal ground control point; d. example of airborne thermal image over forested area with ground control points circled.



Speci<sup>fi</sup>cations of imaging instrumentation.


<table><tr><td></td><td>Panasonic Lumix</td><td>Optris PI450</td></tr><tr><td>Lens (FOV)</td><td><eq>46.8^{\circ} \times 32.2^{\circ}</eq></td><td><eq>38^{\circ} \times 29^{\circ}</eq></td></tr><tr><td>Optical resolution</td><td><eq>4608 \times 2592</eq> pixels</td><td><eq>382 \times 288</eq> pixels</td></tr><tr><td>Spectral range</td><td>-</td><td>7.5–13 μm</td></tr><tr><td>Temperature range</td><td>-</td><td>-20–100 °C</td></tr><tr><td>Accuracy</td><td>-</td><td>± 2% or ± 2 °C</td></tr><tr><td>Weight</td><td>560 g</td><td>320 g</td></tr><tr><td>Azimuth during imaging</td><td><eq>0^{\circ}</eq></td><td><eq>0^{\circ}</eq></td></tr></table>

## 3.3. SfM-MVS model generation

A summary of the full work<sup>fl</sup>ow for SfM-MVS (Structure-from Motion multi-view stereo methods) model generation is presented in Fig. 3. Raw thermal .csv <sup>fi</sup>les contained $2 8 8 \times 3 8 2$ cells, each representing the recorded temperature of a pixel from the imager. Previous calibration of the PI450 imager showed a non-uniformity in recorded temperature across the <sup>fi</sup>eld of view which varied $\mathrm { b y } < 2 \mathrm { K } ,$ which is within the manufacturer speci<sup>fi</sup>ed error of the imager (Smiga et al., 2015). Images were therefore not corrected for non-uniformity. 

Raw thermal <sup>fi</sup>les were converted to grayscale .png digital images (382 × 288 pixels) using MATLAB software (R2015) with a temperature (°C) assigned to each pixel (e.g. Fig. 2d). All images from a single <sup>fl</sup>ight were set to have the same color scale. Greyscale images were more desirable over color images as they have a single color channel (compared to a three color channel in RGB images), thus can easily be converted back to a single temperature value. Minimum temperature was set to $0 ~ ^ { \circ } \mathrm { C }$ in all thermal images in order to 1) remove thermal variation at the snow surface and 2) increase the visual contrast of the forest to aid point recognition in 3D model generation. All pixels with a recorded temperature below 0°C were therefore not included in further analysis. Air temperature during imaging was above $0 \ { } ^ { \circ } { \bf C } ,$ thus it was assumed canopy temperature was also warmer than the snow surface temperature (Jarvis et al., 1976). Snow-covered ground was automatically masked in the RGB and thermal photosets for the forest stand site and were excluded from scene reconstruction. Ground conditions were entirely snow-free at the single tree site. 

RGB and thermal datasets were processed separately in Agisoft PhotoScan Professional Edition software (2015, v. 1.1.6). PhotoScan employs a standard SfM-MVS work<sup>fl</sup>ow, beginning with the identi<sup>fi</sup>- cation of unique image key points and the assignment of key point descriptors, which are stable under variations in perspective and illumination. Key point descriptors were used to establish key point correspondences between photographs (Lowe, 2004), before an iterative, self-calibrating bundle adjustment was used to solve for internal and external camera orientation parameters and produced a sparse, or coarse, 3D point-cloud. Following initial camera alignment and sparse scene reconstruction, 3D points with a reprojection error $> ~ 0 . 5$ pixels were removed, as were points which were visible in fewer than three photographs. The point-cloud data were transformed to the Swiss grid co-ordinate system (CH1903+/LV95) through the identi<sup>fi</sup>cation of known GCP locations. These GCPs provided additional scene control and were used to improve the estimation of camera orientation parameters and reduce model alignment errors using PhotoScan's ‘optimization’ tool. Whilst each set of images were not digitally geotagged during acquisition, the photogrammetrically reconstructed xyz positions of the RGB photographs were exported and used to estimate initial camera positions for the corresponding thermal images, with an associated accuracy bu<sup>f</sup>er $\mathbf { o f } \pm \mathbf { \nabla } 2 \mathbf { m }$ . This additional and often non-standard SfM-MVS processing step improved the accuracy and processing speed of the initial camera alignment and retrieval of the lens distortion parameters for the thermal imager. Following project georegistration and optimization, dense point-cloud reconstruction was undertaken using MVS methods, which increased point densities by over an order of magnitude. The reconstruction ‘quality’, for the dense point-clouds was specified as ‘ultra-high’ for all models, which ensures that the thermal 


Table 2


![image](https://cdn-mineru.openxlab.org.cn/result/2026-09-22/88455dc8-52f5-45be-aa4a-0962988e173b/437899fd9cb6614defc369942ed16124845a21fff1856c454b857767bedd86bd.jpg)



Fig. 3. Data collection and SfM-MVS processing work<sup>fl</sup>ow for constructing georeferenced 3D point-clouds of forest structures from coincident RGB and thermal infrared imagery acquired using a lightweight UAS. Steps colored in gray were applied exclusively to thermal data.


information for a given point has been retrieved from the original input images, with no image downscaling and associated averaging of thermal data (Agisoft, 2016). Dense point-clouds were manually scrutinized in CloudCompare (v.2.6) software to remove errors, followed by the application of a statistical outlier removal algorithm to eliminate points which are further away than the mean distance between the six nearest neighboring points. Finally, site-speci<sup>fi</sup>c RGB and thermal 3D datasets were co-registered using iterative closest point (ICP) methods (Srinivasan et al., 2014). Project alignment statistics are displayed in Table 2. 

Following ICP alignment, the grayscale value of each thermally reconstructed 3D point was back-calculated to temperature (°C) from the 8-bit grayscale image using: 

$$
T _ {(x, y)} = (G L _ {(x, y)} \bullet T _ {r a n g e}) - T _ {m i n}\tag{1}
$$

where $T _ { ( x , y ) }$ is the calculated temperature of each point (x,y); $G L _ { ( x , y ) }$ is the gray level of the point (x,y) in the point cloud, which is comprised of X,Y,Z and GL information at each point; $T _ { r a n g e }$ is the di<sup>f</sup>erence between maximum and minimum temperature in the point cloud; and $T _ { m i n }$ is the minimum temperature. $T _ { r a n g e }$ was pre-determined from the raw data <sup>fi</sup>les during initial conversion to grayscale images. 

## 3.4. Aerial LiDAR

LiDAR data over the Davos Laret site were collected in September 2010 using a Riegl LMS Q560 sensor from multiple helicopter <sup>fl</sup>yovers at a nominal <sup>fl</sup>ying altitude of 700 m for a total area of ~90 km<sup>−2</sup>. The wavelength emitted was 1550 nm with pulse durations of 5 ns and up to 7 returns were detected per pulse for a maximum scan angle of ± 15°. Post-processing yielded an average echo density of 36 pulses per m<sup>2</sup> of the <sup>fl</sup>yover domain and 19 pulses per square meter for the last returns (shot density) within the domain area. LiDAR data were subsequently decimated to 0.5 horizontal resolution using classi<sup>fi</sup>ed ground returns. 

## 4. Results

## 4.1. Single tree

## 4.1.1. Geometric characterization

In total, 139 RGB photographs and 249 thermal images of the single tree were used as input to SfM-MVS processing, of which 139 and 186 were aligned by PhotoScan. Remaining input thermal images were not aligned or used for 3D scene reconstruction, most likely due to a combination of factors which include the tree canopy appearing in peripheral portions of the image, where distortion e<sup>f</sup>ects are greatest, and poor image texture relative to the remaining images. In such in stances, tie-point identi<sup>fi</sup>cation and image matching become unviable, and these photographs are discarded from the remainder of the reconstruction work<sup>fl</sup>ow. A calibration procedure to correct for this distortion was carried out following Vidas et al. (2012), however it did not increase the number of images retained through the scene reconstruction. Inspection of RGB and thermal 3D point-clouds for the single tree revealed a consistent geometric correspondence between datasets and the tree (Fig. 4a–c). Residual alignment errors were 0.016 m and 


Summary of UAV survey data products. Number of RGB and thermal images in brackets refers to original input images, whilst number without brackets refers to input images which were successfully aligned by Agisoft PhotoScan. Similarly, number in brackets indicate number of GCPs (ground control points) successfully projected and used for RGB 3D reconstruction of both sites, whilst the number without brackets reflects the number of projected ground control point positions in the thermal data.


<table><tr><td rowspan="2">Survey area</td><td rowspan="2">Survey date and time (GMT)</td><td rowspan="2">No. RGB images</td><td rowspan="2">No. thermal images</td><td rowspan="2">Mean <eq>T_{air}</eq>(°C)</td><td rowspan="2">Mean ISWR (<eq>W\ m^{-2}</eq>)</td><td rowspan="2">Solar zenith angle (°)</td><td rowspan="2">No. GCPs</td><td colspan="2">SfM-MVS internal georeferencing error (xyz RMS; m)</td><td rowspan="2">RGB-thermal ICP alignment error (m)</td></tr><tr><td>RGB</td><td>Thermal</td></tr><tr><td>Single tree</td><td>29/04/16 08:55</td><td>139 (139)</td><td>186 (249)</td><td>5.2</td><td>994</td><td>44</td><td>12 (12)</td><td>0.016</td><td>0.081</td><td>0.046</td></tr><tr><td>Forest (1)</td><td>01/04/16 10:45</td><td>165 (165)</td><td>53 (102)</td><td>8.5</td><td>501</td><td>43</td><td>9 (9)</td><td>0.432</td><td>0.086</td><td>0.167</td></tr><tr><td>Forest (2)</td><td>01/04/16 12:55</td><td></td><td>23 (87)_</td><td>10.4</td><td>553</td><td>46</td><td>6 (9)</td><td></td><td>0.074</td><td>0.150</td></tr></table>

Distance north-south (m) 

![image](https://cdn-mineru.openxlab.org.cn/result/2026-09-22/88455dc8-52f5-45be-aa4a-0962988e173b/abb85671fe850a179d86d9adcdfa6082f029d870d5a3203a66987accae73f6b4.jpg)



Fig. 4. North-south pro<sup>fi</sup>le of the single tree: a. RGB image of single tree taken looking east; b. RGB point-cloud dataset; c. thermal point-cloud dataset before cloud-to-cloud <sup>fi</sup>ltering and d. thermal point-cloud dataset after cloud-to-cloud <sup>fi</sup>ltering.


0.081 m for the RGB and thermal datasets, respectively, and indicate good internal consistency for point-cloud reconstruction and georegistration (Table 2). Measured positions of the GCPs around the base of the tree varied by 2.14 m in the vertical (z) plane covering only 8% of the total vertical distance in the 3D scene of the tree (18 m). This limited elevation range does not appear to have had a detrimental e<sup>f</sup>ect on the accuracy of the vertical component of the 3D reconstruction and alignment; the mean cloud-to-cloud distance between RGB and thermal reconstructed 3D point-clouds was 0.046 m. No obvious systematic model doming or deformation e<sup>f</sup>ects were observed (James and Robson, 2012). Both the RGB and thermal point-clouds reconstructed elements of 3D canopy structure across the full height of the tree. 3D point clusters generally corresponded to individual branches, or branch clusters, which were visible from the nadir view perspective of each imaging sensor. 

Occlusion of underlying canopy by skyward-facing branches largely accounted for intermittency of the 3D reconstruction across the full height and interior of the tree in both datasets (Fig. 4b–c). The largest data gap, found on the western edge of the tree, is attributed to heavy shadowing from shortwave radiation at the time of data acquisition, when the sun was in the south-east. Such shading caused issues with key point identi<sup>fi</sup>cation, matching, and scene reconstruction due to the comparatively homogenous textural signature of the shaded area in RGB imagery. Similar errors were seen in the thermal point-cloud, where the lack of thermal variation, and therefore image texture and contrast, resulted in a gap in the thermal point-cloud corresponding to the same location in the RGB point-cloud. 

## 4.1.2. Thermal point-cloud refinement

RGB point-cloud data closely matched the physical structure of the single tree, particularly in the absence of points between the ground and base of the tree canopy, in agreement with real-world tree structure (Fig. 4b; ~1526 m to 1528 m a.s.l.). The occlusion of the tree trunk from the perspective of a downward-facing camera meant that the SfM-MVS model was unable to reconstruct its position. Within the equivalent thermal data, however, the area between ~1526–1528 m contained numerous 3D points (Fig. 4c). Additionally, there is a presence of thermal 3D points between branch clusters, which otherwise remain empty in the RGB 3D data (Fig. 4c). 

A further inconsistency between RGB and thermal point-clouds was an increase in the number of points in the thermal point-cloud, between 1528 and 1530 m, which did not match the physical position of the lower tree branch clusters. On closer inspection, the thermal signature of these additional points had more in common with the surrounding snow-free ground surface, which generally had a higher temperature relative to the tree in areas exposed to direct sunlight, and a lower relative temperature in the shaded, north-western sector of the model. These incorrectly placed points could be attributed to a number of factors, such as the comparatively homogenous texture of the ground surface in the thermal imagery. A further cause of the incorrectly placed points could be the pixel footprint size, which is likely to have proved challenging for accurate depth reconstruction. This predominantly occurs because a single pixel in the thermal imagery encompasses elements of both canopy and the ground, leading to the di<sup>f</sup>erent components being averaged into a single pixel. The result is the incorrect placement of these points in the vertical (z) plane and an arti<sup>fi</sup>cially increased point density, especially in the lower portions of the thermal point-cloud. Additionally, the <sup>fi</sup>eld of view of both the RGB camera and the thermal imager are such that interior canopy detail often appears at the periphery of the input imagery, where the view perspective becomes increasingly oblique (assuming that the image has a nadir orientation) and where the magnitude of lens distortion increases. Scrutiny of the thermal point cloud of the standalone tree reveals that these incorrectly placed points are concentrated towards the interior of the lower canopy. It is feasible that inaccuracies in the estimated in terior camera lens distortion parameters translate into poor positional accuracy for 3D points which are identi<sup>fi</sup>ed and matched across marginal areas of the input thermal imagery. 

In light of these results, the thermal point-cloud was therefore fur ther re<sup>fi</sup>ned by the inclusion of an additional post-processing step, whereby the RGB point-cloud was used to <sup>fi</sup>lter points from the coin cident thermal data. RGB-to-thermal cloud-to-cloud (C2C) distances were calculated in CloudCompare software, and thermal points were iteratively retained or removed depending on their 3D position within a given Euclidean distance threshold of an RGB point. Reducing the threshold distance resulted in a linear reduction in the number of retained points, as well as a reduction in the overall mean and median cloud-to-cloud distance (Table 3; Fig. 4). Importantly, even with the application of a coarse (0.50 m) C2C distance tolerance, the empty volume between the ground surface and base of the canopy was resolved in the thermal data (Fig. 5). Further decreases in the C2C threshold distance from 50 cm down to 10 cm modi<sup>fi</sup>ed the mean vertical temperature pro<sup>fi</sup>le in the lower section of the model (red lines in Fig. 5). This decrease re<sup>fl</sup>ected the removal of ground points (warmer) that were erroneously classi<sup>fi</sup>ed as tree points during SfM-MVS post processing. The use of a 0.1 m threshold resulted in removal of up to $\sim 5 0 \%$ of the thermal data points. However, this resulted in no sub stantial modi<sup>fi</sup>cation to the vertical temperature pro<sup>fi</sup>le in the highest two thirds of the tree (Fig. 5). 


Summary statistics for point cloud reduction following cloud-to-cloud distance thresh olding.


<table><tr><td>C2C threshold distance (m)</td><td>n points</td><td>% points retained</td><td>Mean C2C distance (m)</td><td>Median C2C distance (m)</td></tr><tr><td>Raw</td><td>59,167</td><td>100</td><td>0.194</td><td>0.098</td></tr><tr><td>0.50</td><td>52,807</td><td>89</td><td>0.121</td><td>0.083</td></tr><tr><td>0.45</td><td>51,869</td><td>88</td><td>0.108</td><td>0.078</td></tr><tr><td>0.40</td><td>50,733</td><td>86</td><td>0.108</td><td>0.078</td></tr><tr><td>0.35</td><td>49,293</td><td>83</td><td>0.100</td><td>0.075</td></tr><tr><td>0.30</td><td>47,747</td><td>81</td><td>0.093</td><td>0.072</td></tr><tr><td>0.25</td><td>45,646</td><td>77</td><td>0.085</td><td>0.068</td></tr><tr><td>0.20</td><td>42,434</td><td>72</td><td>0.074</td><td>0.062</td></tr><tr><td>0.15</td><td>37,698</td><td>64</td><td>0.062</td><td>0.055</td></tr><tr><td>0.10</td><td>30,077</td><td>51</td><td>0.046</td><td>0.043</td></tr></table>

## 4.1.3. Thermal characterization

Temperature pro<sup>fi</sup>les of the single tree are shown in Fig. 6. Average air temperature during the data acquisition period, measured at a weather station located 2 km up-valley to the north-west, was $5 . 2 ~ ^ { \circ } \mathrm { C } .$ Tree and ground temperatures in the entire point-cloud ranged from 0.3 to $2 0 ~ ^ { \circ } \mathrm { C }$ and were warmer in the lower third of the tree (1527–1530 m) compared to the upper two thirds. Vertical pro<sup>fi</sup>les show only a small number of points in the north and west (shaded) sectors of the 3D thermal model. Most points within the thermal point-clouds were lo cated at the base and top of the tree, and along the south and east 

(sunny) sides. 

Division of the thermal point-cloud into its cardinal quadrants revealed di<sup>f</sup>erences in vertical temperature pro<sup>fi</sup>les between aspects (Fig. 6c–f). Temperatures were highest in the lower third of the tree in the north, east and south pro<sup>fi</sup>les, and data from this region of the tree were missing in the west quadrant due to the self-shading. Overal highest temperatures were recorded in the south and east quadrants where average temperatures reached up to ${ 1 5 } ^ { \circ } \mathrm { C } ,$ re<sup>fl</sup>ecting the direc tion of exposure of the tree to direct solar radiation. Temperatures in the north and west quadrants were comparatively lower. Above 1530 m (the upper two-thirds of the tree), vertical temperature pro<sup>fi</sup>les were relatively consistent between all four quadrants, and ranged between 7 and $8 ^ { \circ } \mathrm { C } ,$ on average $_ 2 \textrm { ‰}$ above measured air temperature. 

Ground temperatures also di<sup>f</sup>ered between the four quadrants. In particular, the ground in the west quadrant was coldest, ranging between 0 and $_ { 1 0 \mathrm { ~ } ^ { \circ } \mathrm { C } }$ as a result of shading from the tree. The ground in the north was warmer, between 5 and ${ 1 5 } ^ { \circ } \mathrm { C } ,$ as a result of direct shortwave radiation earlier in the day when the direct shortwave radiation was closer to the east of the tree. The cloud-to-cloud <sup>fi</sup>ltering process appears to have removed all ground points within the east and south quadrants. On closer inspection of the raw C2C results, it appear that greater local C2C distances (up to 50 cm) are reported in the vicinity of the ground surface in these quadrants, implying weaker geometric correspondence between the dense RGB and thermal 3D datasets. Scrutiny of the RGB and thermal imagery for the single tree over<sup>fl</sup>ight reveals that fewer photographs of the lower portions of the tree are captured in these quadrants, which may have lowered the reconstruction accuracy. Such issues might be resolved with a revised <sup>fl</sup>ightplan that more equally captures the tree geometry, including the acquisition of additional, oblique imagery. 

## 4.2. Forest stand

## 4.2.1. Geometric and thermal characterization

Two <sup>fl</sup>ights were carried out over the forest stand area on 1 April 

![image](https://cdn-mineru.openxlab.org.cn/result/2026-09-22/88455dc8-52f5-45be-aa4a-0962988e173b/cbf99750c69b4d495f0e47f694c3db6167068faceb43f2d7ff01964591a6003b.jpg)



Fig. 5. Point densities through <sup>fi</sup>ltering procedure using cloud-to-cloud distances between RGB and thermal points


![image](https://cdn-mineru.openxlab.org.cn/result/2026-09-22/88455dc8-52f5-45be-aa4a-0962988e173b/c954e73f0c411c836bab347cc6406c5f7a0bfeb868b48485aa25ca4fe7deabe8.jpg)


![image](https://cdn-mineru.openxlab.org.cn/result/2026-09-22/88455dc8-52f5-45be-aa4a-0962988e173b/41302874e88fbda2957f355fb15c09036e6270b794f04dd6cb644e901585ba56.jpg)


![image](https://cdn-mineru.openxlab.org.cn/result/2026-09-22/88455dc8-52f5-45be-aa4a-0962988e173b/85c532656df07825200577f26f4850f6344c0b559a7ef3ae019ab1185931d036.jpg)



Fig. 6. East-west (a) and north-south (b) perspectives of thermal point-cloud demonstrating temperature distribution of the 3D tree reconstruction. Bottom panel (c–f) demonstrates temperature distribution with height in each of the four cardinal direction wedges. Red lines represent average temperature through the vertical pro<sup>fi</sup>le.


2016 at 10:45 and 12:55. Initial SfM-MVS reconstruction used the RGB images obtained during both <sup>fl</sup>ights in order to increase point-cloud density and reduce gaps in the point-cloud resulting from solar shading of canopy structures. Whilst incorporating images from multiple <sup>fl</sup>ights is appropriate for RGB imagery where the structure and appearance of a scene remains constant, separate thermal 3D point-clouds were generated for each of the two <sup>fl</sup>ights due to temporal evolution of canopy surface temperatures between <sup>fl</sup>ights. SfM-MVS reconstruction yielded 16.8 million 3D points for the RGB photoset, and 206,500 and 148,300 3D points for the two thermal <sup>fl</sup>ights. By comparison, LiDAR data of the <sup>fl</sup>ight area yielded approximately 63,000 points, including ground returns, which were excluded from thermal and RGB datasets due to masking of the snow surface prior to point-cloud generation. The internal georeferencing error for the RGB forest <sup>fl</sup>ight data was 0.432 m, and sub-decimeter for the thermal data (Table 2). Residual errors for subsequent RGB-thermal ICP alignment were 0.167 m and 0.150 m for thermal <sup>fl</sup>ight 1 and 2, respectively. It is noted that, whilst the internal georeferencing error for the RGB data is substantially higher than the equivalent thermal data, only 52% and 26% of the thermal photographs were successfully aligned during bundle adjustment in PhotoScan, whereas 100% of the RGB input photographs were aligned. Further, only 6 of 9 GCPs were successfully projected and used for georeferencing of the thermal dataset from the second UAV <sup>fl</sup>ight due to issues with high wind speeds, which precluded the capture of stable imagery in the south-eastern sector of the forest site. Without any independent data to verify the accuracy of the data, caution is advised in interpreting these metrics in a manner which suggests that the RGB data outperform the corresponding thermal data in terms of internal model consistency or accuracy. 

Comparison of RGB and thermal 3D point-clouds with equivalent LiDAR data over the <sup>fl</sup>ight area demonstrated a much greater pointcloud density of the RGB and thermal SfM-MVS data (Figure). Even with 3D ground points removed from the RGB and thermal datasets, point densities for the clouds shown in Fig. 7 were 35,254 and 776 points per $\mathbf { m } ^ { - 2 } ,$ , respectively, compared to 78 points per $\mathbf { m } ^ { - 2 }$ for the LiDAR point-cloud. Trees in the north-east of the <sup>fl</sup>ight area were not present in the thermal point cloud compared to the RGB and LiDAR point clouds. Despite di<sup>f</sup>erences in point-cloud densities and lower areal coverage in the thermal point cloud, canopy structures and tree clusters were well represented in all three methods. 

Di<sup>f</sup>erences in overlap of the three point-clouds are shown in Figure, along the cross-section shown in Fig. 7. The upper canopy is particu larly well represented by all three methods, although it is represented in greater detail in both the RGB and thermal point-clouds. Although sparser, the LiDAR point-cloud does not appear to misrepresent any element of the canopy structure compared to the RGB and thermal SfM-

![image](https://cdn-mineru.openxlab.org.cn/result/2026-09-22/88455dc8-52f5-45be-aa4a-0962988e173b/72081f47113721cc5cdbaee9ff2d4df0f362310b6ee7167e9cc9efb5ee3c6fdb.jpg)


![image](https://cdn-mineru.openxlab.org.cn/result/2026-09-22/88455dc8-52f5-45be-aa4a-0962988e173b/617cae9b80c3c6674125aaef089564db900f0f09629f937d9bf4096719ce5790.jpg)


![image](https://cdn-mineru.openxlab.org.cn/result/2026-09-22/88455dc8-52f5-45be-aa4a-0962988e173b/59e29cedd788af355fd08ca9dd2922cefed7d7e7905140fec1b45a570c6ad1f0.jpg)


MVS point-clouds. 

## 4.2.2. Temporal characterization

Repeat <sup>fl</sup>ights across the two-hour period on 1 April demonstrated increasing canopy temperatures between 10:45 and 12:55 (Fig. 9). The maximum forest temperature during <sup>fl</sup>ight 1 was $1 7 . 5 ^ { \circ } \mathrm { C } ,$ which increased to $1 9 . 8 ~ ^ { \circ } \mathrm { C }$ during <sup>fl</sup>ight 2. Increased forest temperature corresponded to an increase in local air temperature between 8.5 and $1 0 . 4 ~ ^ { \circ } \mathrm { C }$ between the two <sup>fl</sup>ights. Furthermore, the crowns of the trees were uniformly warmer during <sup>fl</sup>ight 2 compared to <sup>fl</sup>ight 1. In particular, warming at the top of the canopy during <sup>fl</sup>ight 1 was concentrated along south-east-facing sides of the trees (similar to the single tree), whilst canopy temperatures were relatively uniform around tree crowns in all directions during <sup>fl</sup>ight 2. These patterns accurately re<sup>fl</sup>ect the response of the canopy to increased exposure to direct shortwave radiation, particularly due to the increased solar elevation angle. 

Two vertical pro<sup>fi</sup>les of average canopy temperatures (Fig. 10) taken from overlapping areas of the point-clouds (dashed box outline in Fig. 9) show cooler surface temperatures in the lower canopy compared to the upper canopy. Average canopy temperatures during <sup>fl</sup>ight 1 increased from $6 . 7 – 9 . 7 \ ^ { \circ } \mathrm { C }$ in the lower 10 m, up to $1 1 . 8 ~ ^ { \circ } \mathrm { C }$ at the top of the canopy. By comparison, surface temperatures during <sup>fl</sup>ight 2 ranged between 9.9 and $1 2 . 3 ~ ^ { \circ } \mathrm { C }$ in the lower $1 0 \mathrm { m } ,$ increasing to $1 5 . 6 ~ ^ { \circ } \mathrm { C }$ at the top of the canopy. The vertical canopy temperature pro<sup>fi</sup>les show an overall canopy warming of $_ { 1 - 4 } \mathrm { ~ } ^ { \circ } \mathrm { C }$ between 10:45 and 12:55. Warming was greatest in the upper pro<sup>fi</sup>le of the canopy, where increases in average tree crown temperature were approximately $4 ^ { \circ } \mathrm { C } .$ . Temperature increases in the lower 10 m of the canopy (relatively shaded) were between 1 and $2 \ ^ { \circ } \mathrm { C }$ 

## 5. Discussion

## 5.1. Generating 3D point-clouds offorest structures

RGB and thermal point-clouds generated in this study further demonstrate the suitability of UAV-acquired RGB imagery combined with SfM-MVS processing methods for retrieving accurate models of forest canopy structures (Dandois and Ellis, 2013; Wallace et al., 2016). In particular, the high density of the RGB point-clouds of both the single tree and the forest stand, demonstrate an e<sup>f</sup>ective method for characterizing conifer forest structures. At both <sup>fi</sup>eld sites, the geometric characterization of tree structures from thermal SfM-MVS models was su<sup>fi</sup>ciently detailed to permit the identi<sup>fi</sup>cation of individual branch clusters. 

Discrepancies in the number of 3D points in the RGB and thermal point clouds recovered during SfM-MVS processing are explained, in the <sup>fi</sup>rst instance, as a function of the vastly di<sup>f</sup>erent image resolutions; 4608 × 2592 pixels for the RGB sensor and 288 × 382 pixels for the thermal imager. The pixel density of the RGB sensor exceeds the thermal sensor by an order of magnitude, resulting in the identi<sup>fi</sup>cation of fewer image key points for a given pair of corresponding RGB and thermal images. It is likely, however, that the use of a higher resolution thermal imagery or a lower <sup>fl</sup>ying height would reduce these discrepancies. 

Of the 186 thermal images acquired during Flight 1, 249 (75%) aligned to form the thermal point cloud, compared to 100% of the RGB images being included in the RGB point clouds. This limited alignment of thermal images is likely a combination of two artifacts of the thermal imager. The <sup>fi</sup>rst is simply due to the lower resolution of the camera in combination with the changing viewpoint as the UAV moves across the forested area. Trunks of trees are visible in the outer regions of images, however when the tree is in the center of the image the trunk is largely obscured from the imager, as at the single tree. The second explanation is also due to the changing angles of the viewpoint of the imager, which alters the area over which a single pixel averages for one temperature, thus changing the temperature of the object of interest between sequential images. These errors could be avoided through <sup>fl</sup>ying higher and using a camera with a higher pixel resolution or angular view. 

![image](https://cdn-mineru.openxlab.org.cn/result/2026-09-22/88455dc8-52f5-45be-aa4a-0962988e173b/b50ad4e88487084456e9ecb0373b32b3c64cfa821d57e4a57c8d3896aa0f96c8.jpg)



Fig. 8. Cross-sections (Fig. 7) of a 22 × 5 m swath of forest (south-north)at the Laret forest stand site produced from RGB SfM-MVS methods compared to LiDAR (a) and thermal SfM-MVS methods (b). Note horizontal scale exaggerated relative to vertical scale.


Areal coverage of the thermal point clouds compared to the equivalent RGB point clouds was also smaller, particularly in the northwest of the <sup>fl</sup>ight area during <sup>fl</sup>ight 1 and in the south-east of the <sup>fl</sup>ight area during <sup>fl</sup>ight 2. The RGB camera used here had a much greater <sup>fi</sup>eld of view compared to the thermal camera, capturing a larger area of the forest. This allowed for calculation of more key points compared to the limited <sup>fi</sup>eld of view of the thermal imager, particularly in the areas around the edge of the <sup>fl</sup>ight area where canopy features were in a smaller number of thermal images compared to the RGB images. 

![image](https://cdn-mineru.openxlab.org.cn/result/2026-09-22/88455dc8-52f5-45be-aa4a-0962988e173b/cb484ab5465bf1d10a66c3cb51c873fac3a9f044f7971fec4f72e3cc848c95b3.jpg)


SfM-MVS reconstruction of the single tree revealed the presence of incorrectly placed 3D points in the thermal data. Closer inspection of the thermal signature of these incorrectly placed points revealed them to be associated with the ground surface (grass), which was warmer than the tree canopy. The abundance of incorrectly placed 3D thermal points, or false positives, might be explained by the ‘mixed pixel’ phenomenon, where a pixel incorporates the temperature both of the canopy and ground surface. The lower resolution of the thermal imager and resulting blurred edge de<sup>fi</sup>nition of the tree structure in the thermal images remains a challenge for accurate depth reconstruction. Similarly, generation of false image matching parallaxes, resulting from slight displacement of image features because of wind-driven canopy movement, may be an additional factor. However, these e<sup>f</sup>ects were minimized by the simultaneous acquisition of RGB and thermal images. User-guided <sup>fi</sup>ltering of thermal point-cloud data using the coincident RGB 3D model proved to be a highly e<sup>f</sup>ective way of removing most incorrectly placed points, but inevitably it can also remove accurately placed thermal data. The combination of a high quality RGB camera, used coincidentally with the thermal camera can overcome some of the apparent issues associated with using a lower resolution imager to capture thermal data and represents a substantial technological advancement. Furthermore, it is likely that future improvements in lightweight, survey grade thermal sensor technology, speci<sup>fi</sup>cally sensor resolution and <sup>fi</sup>delity, will improve the robustness of 3D reconstruc tion. 

![image](https://cdn-mineru.openxlab.org.cn/result/2026-09-22/88455dc8-52f5-45be-aa4a-0962988e173b/58a9c0f27fb5c18891801fad53c38e1a28e5871f3364443a0e438d2924f6227e.jpg)



Fig. 9. Top-down view of the thermal point-clouds generated from Flight 1 and Flight 2 colored by temperature. Dashed box indicates area over which temperatures were averaged for vertical pro<sup>fi</sup>les shown in Fig. 10. Arrows indicate solar azimuth and direction of direct shortwave radiation.


![image](https://cdn-mineru.openxlab.org.cn/result/2026-09-22/88455dc8-52f5-45be-aa4a-0962988e173b/16cf1b557e3287509009dab451090a9f7a8a06fa2589a9aea7c4c7c6b17cb471.jpg)


![image](https://cdn-mineru.openxlab.org.cn/result/2026-09-22/88455dc8-52f5-45be-aa4a-0962988e173b/a400f39592d29ab9f96684317465d58e7ae11273aa5105f71e8161f8e2069d34.jpg)


![image](https://cdn-mineru.openxlab.org.cn/result/2026-09-22/88455dc8-52f5-45be-aa4a-0962988e173b/55cbee5687c90d51f77d234b7c3a491467a8275d78c9d376d54dc2b6b6f46fc2.jpg)



Fig. 10. Average vertical canopy temperature pro<sup>fi</sup>le of each <sup>fl</sup>ight averaged across the overlapping area shown in Fig. 9. Air temperature and incoming shortwave radiation from the weather station at the open site are shown and times of each <sup>fl</sup>ight are indicated by vertical lines.


The high density of the RGB point-clouds, when compared to the LiDAR data over the same forest stand, represent an improvement on current methods for obtaining information on forest structures. Pointcloud densities between 20 and 67 points per m<sup>2</sup> for LiDAR and SfMderived datasets, respectively, have been presented in previous UAV-SfM-based studies of forest structures (e.g. Dandois and Ellis, 2013), compared to 78 and 35,245 points m<sup>2</sup> presented in this study, an increase in density of 452%. The increased point densities in this study are attributed to di<sup>f</sup>erences in above-canopy <sup>fl</sup>ying heights which were generally far lower than existing studies. A necessary trade-o<sup>f</sup> exists between areal coverage, which is primarily a function of <sup>fl</sup>ying height and sensor view-shed, and point-cloud density or resolution. Increased areal coverage is achievable through increased UAV <sup>fl</sup>ying height and range, whilst preserving data densities and accuracies which are achievable by surveying at low altitudes is only possible through the use of increased image sensor resolution. Consequently, further work is required to fully explore the potential of areal upscaling from the scale of individual trees and small forest stands, to geometric and thermal characterization of entire forests and plantations. 

The LiDAR point-cloud information used in this study has previously been applied to the derivation of canopy structure metrics (Moeser et al., 2015a) and the development of a snow interception model (Moeser et al., 2015b). Further a<sup>fi</sup>eld, LiDAR data of forest structures have successfully been used for mapping landscape-scale conifer forest structures, improving on lower resolution satellite methods (Morsdorf et al., 2006; Solberg et al., 2009). The accuracy and resolution of RGB imagery point-clouds presented in this study compared to LiDAR sug gest methods for mapping forest structures previously developed using 

LiDAR data can be suitably be applied using RGB point-clouds where LiDAR data are unavailable. In particular, the data acquisition time in this study (< 10 min) demonstrates the ease at which 3D canopy structure information can be obtained across forest stand scales. Spe ci<sup>fi</sup>cally, the use of RGB point-clouds combined with the increased affordability and accessibility of UAV technologies are likely to make forest structure metrics such as e<sup>f</sup>ective leaf area index (Solberg et al., 2009) and fractional forest cover (Morsdorf et al., 2006) more straightforward to obtain in the future. 

## 5.2. Thermal analysis of forest canopies using remote sensing

Canopy temperatures are less commonly measured than air temperatures, despite a strong relevance in radiation and biogeochemical cycles in forested environments. Previous studies have used groundbased IR imagery to capture canopy temperatures due to their relationship with meteorological variations such as air temperature and solar radiation (Howard and Stull, 2013; Pomeroy et al., 2009). This study signi<sup>fi</sup>cantly advances the ability to remotely quantify spatial and temporal variations in forest canopy temperatures through the use of 3D models derived from coarse resolution thermal imagery. It builds upon the existing use of 2D mapping methods (e.g. Faye et al., 2016), which restricts post-analysis, interpretation and application to only the horizontal dimension. Additionally, it improves on existing research applications of 3D thermal data which map 2D thermographic information onto RGB or LiDAR-derived 3D topographic models (e.g. Luscombe et al., 2015; Nishar et al., 2016); however, such an approach is unsuitable for geometrically complex environments such as forests. 

3D thermal reconstruction of the single tree demonstrated both horizontal and vertical variations in surface temperatures. The model accurately captured warmer temperatures in the eastern and southern sectors of the tree, where it was exposed to direct solar heating, and cooler temperatures in the northern and western sectors. Additionally, warmest temperatures were found in the lower third of the tree, likely due to the increased surface area and heat retention capacity of the branches. Canopy temperatures decreased with height in all four quadrants of the tree, resulting in tree temperatures which were on average 2 °C above the measured air temperature. The consistent reduction in canopy surface temperature with increasing height, regardless of direction of exposure to sunlight, can be explained by the small boundary layer resistance of conifer needles, which makes up an increasing proportion of the tree with increasing height. The low resistance (high conductance) to heat transfer by the needles lead to rapid exchange of sensible heat (Jarvis et al., 1976), combined with an increase in wind exposure with increasing height, reducing the average temperature of the upper tree compared to the lower tree which is comprised of more woody elements (trunk and branches) which retain heat more e<sup>fi</sup>ciently. 

Repeat <sup>fl</sup>ights demonstrated canopy temperature variations throughout the stand scale are strongly coupled to incoming shortwave radiation, although this has previously only been demonstrated through ground-based thermal imagery (Pomeroy et al., 2009; Webster et al., 2016). A lack of variation in canopy temperatures around tree crowns during the second <sup>fl</sup>ight over the forested area when compared to <sup>fl</sup>ight 1 demonstrated a more uniform exposure of the canopy crowns to direct heating by solar radiation as a result of increased solar angle between the two <sup>fl</sup>ights. Earlier in the morning, the canopy was only exposed to direct solar radiation in areas facing southeast. As the solar angle increases, tree crowns become increasingly exposed in all directions. This is particularly relevant along shaded sides of forest gaps or clearings and edges, as exposure to shortwave radiation from above and behind leads to warmer temperatures in the upper canopy compared to the lower canopy (Webster et al., 2017). Vertical pro<sup>fi</sup>les of average canopy temperature also imply that exposure to solar radiation has a stronger in<sup>fl</sup>uence on vertical canopy temperature pro<sup>fi</sup>les in forested areas where the lower canopy is often shaded. An additional process in<sup>fl</sup>uencing temperature distribution in canopies is that the irradiance to the lower canopy from the ground is typically less than the irradiance from the atmosphere to the upper canopy. These 3D results presented here demonstrate multiple layers in the vertical variation of the canopy energy balance. 

## 5.3. Wider applications of thermal imagery

Airborne thermal imagery of the 30 × 30 m forest site in this study revealed horizontal and vertical variation in canopy surface temperatures ranging from 1 to $2 0 ~ ^ { \circ } \mathrm { C } .$ . The methods presented here therefore work to improve understanding of the sub-grid heterogeneity of canopy temperatures in relation to coarser scale satellite products. For example, satellite infrared remote sensing of surface temperatures is currently limited to 90 m pixel resolution (ASTER, Yamaguchi et al., 1998), often missing critical sub-grid scale temperature variations such as those demonstrated here. The methods presented here therefore increase the capacity to combine high spatial and temporal resolution data to improve interpretation of satellite information across landscape scales. Extension of these localized methods to application at larger landscape scales can be facilitated through improved knowledge regarding the vertical canopy temperature pro<sup>fi</sup>les. These pro<sup>fi</sup>les can be integrated with satellite land surface temperature information that ultimately provides the average top of canopy temperature within each pixel. A known relationship between the temperatures of the upper and lower canopy can facilitate the use of canopy temperature in larger scale radiative models using airborne or satellite measurements as input vari ables. Applying calculated vertical temperature pro<sup>fi</sup>les to satellite information of canopy temperatures thus provides sub-canopy temperature information across larger spatial scales for input into local to regional to hemisphere scale land surface models. 

The methodology presented in this paper demonstrates the ability to capture 3D thermal information of forest canopy structure at the stand scale. These methods can be applied within a number of environmental applications, including energy balance modeling, particularly longwave radiation (Essery et al., 2008b), evapotranspiration prediction (Leinonen et al., 2006) and crop-stress detection (Berni et al., 2009). Additionally, these UAV imaging and post-processing techniques are equally applicable to enhance remote measurement of largely inaccessible physical environments, where 3D thermal data may be of use for advanced process analysis, such as glacier surfaces (Bhardwaj et al., 2016) or areas of volcanic and geothermal activity (Mori et al., 2016; Nishar et al., 2016). 

## 6. Conclusions

Coincident thermal and RGB imagery from a UAV were used to produce 3D RGB and thermal models of standalone trees and forest stands. SfM-MVS methods were used to accurately recover 3D forest canopy thermal structure from thermal imagery. Although thermal imagery was lower in point density than coincident RGB images, thermal 3D point-clouds of both the standalone tree and forest site accurately reproduced complex upper-canopy structures. However, the coarse resolution of thermal imagery proved challenging for accurate depth reconstruction of 3D points in the lower forest canopy. These issues could be resolved through the combination of the high quality RGB point cloud and cloud-to-cloud <sup>fi</sup>ltering processes to remove incorrectly placed thermal points created through mixed pixels. 

RGB and thermal imagery from two UAV <sup>fl</sup>ights were acquired of a 30 × 30 m forest stand on a single morning during the snowmelt season. RGB and thermal point-cloud densities were 35,254 and 776 points per m<sup>−2</sup>, compared to 78 points per m<sup>−2</sup> for a LiDAR dataset of the same area. Thermal point-clouds acquired from two repeat UAV surveys (10:45 and 12:55 on the same day) showed the response of canopy temperatures to increasing shortwave radiation. Warmer average and maximum temperatures were recorded during the second survey. Temperature distributions of tree crowns during the second survey revealed a more uniform temperature distribution and additional heating of shorter trees as a response to increased solar angle and penetration of shortwave radiation to lower regions of the canopy. Vertical temperature variations demonstrated cooler canopy temperatures in the lower pro<sup>fi</sup>le of the forest stand due to shading by the surrounding canopy, compared to the standalone tree which was sun-lit along the entire vertical pro<sup>fi</sup>le. The ability to quantify 3D surface temperatures of forest canopy structures at high spatial and temporal resolutions has important implications for atmospheric, hydrological and ecological modeling, and has wider applications for thermal measurement of further remote environmental landscapes. 

## Acknowledgements

Field support was given by Giulia Mazotti and Sebastian Würzer of the SLF Snow Hydrology Group. Stuart Dunning is thanked for UAV technical support. Data used in the analysis is permanently archived and can be made available upon request to the corresponding author (clare.webster@northumbria.ac.uk) or the last author (jonas@slf.ch). The authors are grateful to three anonymous reviewers whose comments contributed to improving the manuscript. 

## References



Agisoft, 2016. Agisoft PhotoScan Professional, Edition v.1.2.3. . http://www.agisoft.com. Anderson. M.C., Allen. R.G., Morse, A., Kustas. W.P., 2012. Use of Landsat thermal imagery in monitoring evapotranspiration and managing water resources. Remote Sens, Environ, 122, 50–65. 





Ball, M., Pinkerton, H., 2006. Factors a<sup>f</sup>ecting the accuracy of thermal imaging cameras in volcanology (1978–2012). J. Geophys. Res. Solid Earth 111 (B11). 





Bendig, J., Bolten, A., Bennertz, S., Broscheit, J., Eichfuss, S., Bareth, G., 2014. Estimating biomass of barley using crop surface models (CSMs) derived from UAV-based RGB imaging, Remote Sens. 6. 10395–10412. 





Berni, J.A., Zarco-Tejada, P.J., Suárez, L., Fereres, E., 2009. Thermal and narrowband multispectral remote sensing for vegetation monitoring from an unmanned aeria vehicle JFFFE Geosci Remote Sens Lett 47 722-738 





Bhardwaj, A., Joshi, P., Sam, L., Snehmani, 2016. Remote sensing of alpine glaciers in visible and infrared wavelengths: a survey of advances and prospects. Geocarto Int 31, 557–574. 





Boufama, B., Mohr, R., Veillon, F., 1993 May. Euclidean Constraints for Uncalibrated Reconstruction. Computer Vision, 1993. Proceedings., Fourth International Conference IEEE, pp. 466–470. 





Carrivick, J.L., Smith, M.W., Quincey, D.J., 2016. Structure From Motion in the Geosciences. John Wiley & Sons. 





Cohen, Y., Alchanatis, V., Meron, M., Saranga, Y., Tsipris, J., 2005. Estimation of lea water potential by thermal imagery and spatial analysis. J. Exp. Bot. 56, 1843–1852. 





Dandois, J.P., Ellis. E.C., 2010. Remote sensing of vegetation structure using computer vision Bemote Sens 2. 1157–1176 





Dandois, J.P., Ellis, E.C., 2013. High spatial resolution three-dimensional mapping of vegetation spectral dynamics using computer vision. Remote Sens. Environ. 136, 259–276. 





Erdody, T.L., Moskal, L.M., 2010. Fusion of LiDAR and imagery for estimating forest canopy fuels. Remote Sens. Environ. 114, 725–737. 





Essery, R., Bunting, P., Rowlands, A., Rutter, N., Hardy, J., Melloh, R., Link, T., Marks, D., Pomeroy, J., 2008a. Radiative transfer modeling of a coniferous canopy characterized by airborne remote sensing. J. Hydrometeorol. 9, 228–241. 





Essery, R., Pomeroy, J., Ellis, C., Link, T., 2008b. Modelling longwave radiation to snow beneath forest canopies using hemispherical photography or linear regression. Hydrol. Process. 22, 2788–2800. 





FAO, 2010. Global forest resources assessment 2010: Main repot. In: Ea.A.O.otUN. (Ed) 





Faye, E., Rebaudo, F., Yánez-Cajo, D., Cauvy-Fraunié, S., Dangles, O., 2016. A toolbox for studying thermal heterogeneity across spatial scales: from unmanned aerial vehicle imagery to landscape metrics. Methods Ecol. Evol. 7, 437–446. 





Gago, J., Douthe, C., Coopman, R., Gallego, P., Ribas-Carbo, M., Flexas, J., Escalona, J., Medrano, H., 2015. UAVs challenge to assess water stress for sustainable agriculture. Agric. Water Manag. 153, 9–19. 





Hernández-Clemente, R., Navarro-Cerrillo, R.M., Ramírez, F.J.R., Hornero, A., Zarco-Tejada, P.J., 2014. A novel methodology to estimate single-tree biophysical parameters from 3D digital imagery compared to aerial laser scanner data. Remote Sens. 6, 11627–11648 





Houghton, R., Hall, F., Goetz, S.J., 2009. Importance of biomass in the global carbon cycle. J. Geophys. Res. Biogeosci. 114. 





Howard, R., Stull, R., 2013. IR radiation from trees to a ski run: a case study. J. Appl. Meteorol. Climatol. 52, 1525–1539. 





James, M., Robson, S., 2012. Straightforward reconstruction of 3D surfaces and topography with a camera: accuracy and geoscience application. J. Geophys. Res. Earth Surf. 117. 





James, M.R., Pinkerton, H., Applegarth, L.J., 2009. Detecting the development of active lava <sup>fl</sup>ow <sup>fi</sup>elds with a very-long-range terrestrial laser scanner and thermal imagery. Geophys. Res. Lett. 36. 





Jarvis, P., James, G., Landsberg, J., 1976. Coniferous forest. In: Vegetation and the Atmosphere. 2. pp. 171–240. 





Kankare, V., Vastaranta, M., Holopainen, M., Räty, M., Yu, X., Hyyppä, J., Hyyppä, H., Alho, P., Viitala, R., 2013. Retrieval of forest aboveground biomass and stem volum with airborne scanning LiDAR. Remote Sens. 5, 2257–2274. 





Kobayashi, H., Baldocchi, D.D., Ryu, Y., Chen, Q., Ma, S., Osuna, J.L., Ustin, S.L., 2012. Modeling energy and carbon <sup>fl</sup>uxes in a heterogeneous oak woodland: a three-dimensional approach. Agric. For. Meteorol. 152, 83–100. 





Leinonen, I., Grant, O., Tagliavia, C., Chaves, M., Jones, H., 2006. Estimating stomatal conductance with thermal imagery. Plant Cell Environ. 29, 1508–1518. 





Liang, X., Litkey, P., Hyyppa, J., Kaartinen, H., Vastaranta, M., Holopainen, M., 2012. Automatic stem mapping using single-scan terrestrial laser scanning. IEEE Trans. Geosci, Remote Sens, 50. 661-670 





Lowe, D.G., 2004. Distinctive image features from scale-invariant keypoints. Int. J. Comput. Vis. 60, 91–110. 





Lucas, R., Lee, A., Bunting, P., 2008. Retrieving forest biomass through integration of CASI and LiDAR data. Int. J. Remote Sens. 29. 1553–1577 





Luscombe, D.J., Anderson, K., Gatis, N., Grand-Clement, E., Brazier, R.E., 2015. Using airborne thermal imaging data to measure near-surface hydrology in upland eco: systems. Hydrol. Process. 29, 1656–1668 





Mlambo. R.. Woodhouse. I.. Gerard. F.. Anderson. K., 2017. Structure from motion (SfM) photogrammetry with drone data: a low cost method for monitoring greenhouse gas emissions from forests in developing countries. Forests 8. 68. 





Moeser, D., Morsdorf, F., Jonas, T., 2015a. Novel forest structure metrics from airborne LiDAR data for improved snow interception estimation. Agric. For. Meteorol. 208, 40–49. 





Moeser, D., Stähli, M., Jonas, T., 2015b. Improved snow interception modeling using canopy parameters derived from airborne LIDAR data. Water Resour. Res. 51. 5041–5059. 





Morgenroth, J., Gomez, C., 2014. Assessment of tree structure using a 3D image analysis technique—a proof of concept. Urban For. Urban Green. 13, 198–203. 





Mori, T., Hashimoto, T., Terada, A., Yoshimoto, M., Kazahaya, R., Shinohara, H., Tanaka, R., 2016. Volcanic plume measurements using a UAV for the 2014 Mt. Ontake eruption. Earth Planets Space 68, 49. 





Morsdorf, F., Kötz, B., Meier, E., Itten, K., Allgöwer, B., 2006. Estimation of LAI and fractional cover from small footprint airborne laser scanning data based on gap fraction. Remote Sens. Environ. 104, 50–61. 





Musselman, K.N., Margulis, S.A., Molotch, N.P., 2013. Estimation of solar direct beam transmittance of conifer canopies from airborne LiDAR. Remote Sens. Environ. 136, 402–415. 





Nishar, A., Richards, S., Breen, D., Robertson, J., Breen, B., 2016. Thermal infrared imaging of geothermal environments and by an unmanned aerial vehicle (UAV): a case study of the Wairakei–Tauhara geothermal field, Taupo, New Zealand. Renew. Energy 86, 1256–1264. 





P<sup>fi</sup>ster, L., McDonnell, J.J., Hissler, C., Ho<sup>f</sup>mann, L., 2010. Ground-based thermal imagery as a simple, practical tool for mapping saturated area connectivity and dynamics. Hydrol. Process. 24. 3123–3132. 





Pomeroy, J.W., Marks, D., Link, T., Ellis, C., Hardy, J., Rowlands, A., Granger, R., 2009. The impact of coniferous forest temperature on incoming longwave radiation to melting snow. Hydrol. Process. 23, 2513–2525. 





Price, A., Petzold, D., 1984. Surface emissivities in a boreal forest during snowmelt. Arct. Alp. Res. 45–51. 





Rudol, P., Doherty, P., 2008. Human Body Detection and Geolocalization for UAV Search and Rescue Missions Using color and Thermal Imagery. Aerospace Conference IEEE, pp. 1–8. 





Smigaj, M., Gaulton, R., Barr, S.L., Suárez, J.C., 2015. UAV-borne thermal imaging for forest health monitoring: detection of disease-induced canopy temperature increase. Int. Arch. Photogramm. Remote. Sens. Spat. Inf. Sci. 40 (3), 349. 





Snavely, N., Seitz, S.M., Szeliski, R., 2008. Modeling the world from internet photo collections. Int. J. Comput. Vis. 80, 189–210. 





Solberg, S., Brunner, A., Hanssen, K.H., Lange, H., Næsset, E., Rautiainen, M., Stenberg, P., 2009. Mapping LAI in a Norway spruce forest using airborne laser scanning. Remote Sens. Environ. 113, 2317–2327. 





Spampinato, L., Calvari, S., Oppenheimer, C., Boschi, E., 2011. Volcano surveillance using infrared cameras. Earth Sci. Rev. 106, 63–91. 





Spetsakis, M.E., Aloimonos, Y., 1991. A multi-frame approach to visual motion perception. Int. J. Comput. Vis. 6, 245–255. 





Srinivasan, S., Popescu, S.C., Eriksson, M., Sheridan, R.D., Ku, N.-W., 2014. Multi-temporal terrestrial laser scanning for modeling tree biomass change. For. Ecol. Manag. 318, 304–317. 





Szeliski, R., Kang, S.B., 1994. Recovering 3-D shape and motion from image streams using nonlinear least squares. J. Vis. Commun. Image Represent. 5, 10–28. 





Vidas, S., Lakemond, R., Denman, S., Fookes, C., Sridharan, S., Wark, T., 2012. A maskbased approach for the geometric calibration of thermal-infrared cameras. IEEE Trans. Instrum, Meas, 61 (6). 1625–1635. 





Wagner, W., Hollaus, M., Briese, C., Ducic, V., 2008. 3D vegetation mapping using smallfootprint full-waveform airborne laser scanners, Int, J. Remote Sens. 29. 1433–1452 





Wallace, L., Lucieer, A., Malenovský, Z., Turner, D., Vopěnka, P., 2016. Assessment of forest structure using two UAV techniques: a comparison of airborne laser scanning and structure from motion (SfM) point clouds. Forests 7, 62. 





Webster, C., Rutter, N., Zahner, F., Jonas, T., 2016. Modeling subcanopy incoming longwave radiation to seasonal snow using air and tree trunk temperatures. J Geophys, Res,-Atmos, 121, 1220–1235 





Webster. C.. Rutter, N.. Jonas. T.. 2017. Improving representation of canopy temperatures for modeling subcanopy incoming longwave radiation to the snow surface. J. Geophys. Res. Atmos. 122, 9154–9172. http://dx.doi.org/10.1002/2017JD026581. 





Westoby, M.J., Brasington, J., Glasser, N.F., Hambrey, M.J., Reynolds, J.M., 2012. ‘Structure-from-motion’ photogrammetry: a low-cost, efective tool for geoscience applications. Geomorphology 179, 300–314. 





Yamaguchi, Y., Kahle, A.B., Tsu, H., Kawakami, T., Pniel, M., 1998. Overview of advanced spaceborne thermal emission and re<sup>fl</sup>ection radiometer (ASTER). IEEE Trans. Geosci. Remote Sens. 36, 1062–1071 





Zhao, K., Popescu, S., 2009. Lidar-based mapping of leaf area index and its use for validating GLOBCARBON satellite LAI product in a temperate forest of the southern USA. Remote Sens. Environ113. 1628-1645 

