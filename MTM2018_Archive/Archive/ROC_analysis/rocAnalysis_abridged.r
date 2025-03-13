## Determining optimum NDVI threshold via ROC analysis
## Andrew Pericak, 2016

library(pROC) # There are many libararies that do ROC; this seemed to be recently updated

### Read in data (use included csv files)###
ls58 <- read.csv("F:\\Pericak_Summer16\\Docs\\ROC\\ls58.csv")
ls5 <- read.csv("F:\\Pericak_Summer16\\Docs\\ROC\\ls5.csv")
ls7 <- read.csv("F:\\Pericak_Summer16\\Docs\\ROC\\ls7.csv")
ls8 <- read.csv("F:\\Pericak_Summer16\\Docs\\ROC\\ls8.csv")



### Landsat 5 and 8 combined ###
## These lines create and plot the ROC curve, find the "best" (optimal) threshold, and find the AUC of the curve

# NDVI
curve58_NDVI <- roc(ls58$trueMining, ls58$NDVI, auc = TRUE, plot = TRUE)
bestThresh58_NDVI <- curve58_NDVI$thresholds[which.max(curve58_NDVI$sensitivities + curve58_NDVI$specificities)]
AUCthresh58_NDVI <- round(as.numeric(auc(curve58_NDVI)),4)

# SAVI
curve58_SAVI <- roc(ls58$trueMining, ls58$SAVI, auc = TRUE, plot = TRUE)
bestThresh58_SAVI <- curve58_SAVI$thresholds[which.max(curve58_SAVI$sensitivities + curve58_SAVI$specificities)]
AUCthresh58_SAVI <- round(as.numeric(auc(curve58_SAVI)),4)

curve58_EVI <- roc(ls58$trueMining, ls58$EVI, auc = TRUE, plot = TRUE)
bestThresh58_EVI <- curve58_EVI$thresholds[which.max(curve58_EVI$sensitivities + curve58_EVI$specificities)]
AUCthresh58_EVI <- round(as.numeric(auc(curve58_EVI)),4)



### Landsat 5 only ###

# NDVI
curve5_NDVI <- roc(ls5$trueMining, ls5$NDVI, auc = TRUE, plot = TRUE)
bestThresh5_NDVI <- curve5_NDVI$thresholds[which.max(curve5_NDVI$sensitivities + curve5_NDVI$specificities)]
AUCthresh5_NDVI <- round(as.numeric(auc(curve5_NDVI)),4)

# SAVI
curve5_SAVI <- roc(ls5$trueMining, ls5$SAVI, auc = TRUE, plot = TRUE)
bestThresh5_SAVI <- curve5_SAVI$thresholds[which.max(curve5_SAVI$sensitivities + curve5_SAVI$specificities)]
AUCthresh5_SAVI <- round(as.numeric(auc(curve5_SAVI)),4)

# EVI
curve5_EVI <- roc(ls5$trueMining, ls5$EVI, auc = TRUE, plot = TRUE)
bestThresh5_EVI <- curve5_EVI$thresholds[which.max(curve5_EVI$sensitivities + curve5_EVI$specificities)]
AUCthresh5_EVI <- round(as.numeric(auc(curve5_EVI)),4)



### Landsat 7 only ###

# NDVI
curve7_NDVI <- roc(ls7$trueMining, ls7$NDVI, auc = TRUE, plot = TRUE)
bestThresh7_NDVI <- curve7_NDVI$thresholds[which.max(curve7_NDVI$sensitivities + curve7_NDVI$specificities)]
AUCthresh7_NDVI <- round(as.numeric(auc(curve7_NDVI)),4)



### Landsat 8 only ###

# NDVI
curve8_NDVI <- roc(ls8$trueMining, ls8$NDVI, auc = TRUE, plot = TRUE)
bestThresh8_NDVI <- curve8_NDVI$thresholds[which.max(curve8_NDVI$sensitivities + curve8_NDVI$specificities)]
AUCthresh8_NDVI <- round(as.numeric(auc(curve8_NDVI)),4)

# SAVI
curve8_SAVI <- roc(ls8$trueMining, ls8$SAVI, auc = TRUE, plot = TRUE)
bestThresh8_SAVI <- curve8_SAVI$thresholds[which.max(curve8_SAVI$sensitivities + curve8_SAVI$specificities)]
AUCthresh8_SAVI <- round(as.numeric(auc(curve8_SAVI)),4)

# EVI
curve8_EVI <- roc(ls8$trueMining, ls8$EVI, auc = TRUE, plot = TRUE)
bestThresh8_EVI <- curve8_EVI$thresholds[which.max(curve8_EVI$sensitivities + curve8_EVI$specificities)]
AUCthresh8_EVI <- round(as.numeric(auc(curve8_EVI)),4)



### Since it appears NDVI is the best measure (per AUC), find the 95% confidence interval for the best threshold
ciThresh58 <- ci.coords(curve58_NDVI, "best", "threshold")
ciThresh5 <- ci.coords(curve5_NDVI, "best", "threshold")
ciThresh7 <- ci.coords(curve7_NDVI, "best", "threshold")
ciThresh8 <- ci.coords(curve8_NDVI, "best", "threshold")



### Get the coordinates (i.e., (specificity, sensitivity)) of the threshold point for the NDVI model
coords58 <- coords(curve58_NDVI, "best", "threshold", c("specificity", "sensitivity"))
coords5 <- coords(curve5_NDVI, "best", "threshold", c("specificity", "sensitivity"))
coords7 <- coords(curve58_NDVI, "best", "threshold", c("specificity", "sensitivity"))
coords8 <- coords(curve8_NDVI, "best", "threshold", c("specificity", "sensitivity"))


### Print all coordinates along ROC curve for the NDVI model
allCoords58 <- coords(curve58_NDVI, "all")
allCoords5 <- coords(curve5_NDVI, "all")
allCoords7 <- coords(curve7_NDVI, "all")
allCoords8 <- coords(curve8_NDVI, "all")
