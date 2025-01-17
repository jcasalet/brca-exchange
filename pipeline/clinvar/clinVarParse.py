#!/usr/bin/env python
"""
clinVarParse: parse the ClinVar XML file and output the data of interest
"""
import argparse
import clinvar
import codecs
import re
import sys
import xml.etree.ElementTree as ET
import logging

def printHeader():
    print("\t".join(("HGVS", "Submitter", "ClinicalSignificance",
                     "DateLastUpdated", "DateSignificanceLastEvaluated", "SCV",
                     "SCV_Version", "ID", "Origin", "Method", "Genomic_Coordinate",
                     "Symbol", "Protein", "Description", "SummaryEvidence",
                     "ReviewStatus", "ConditionType", "ConditionValue",
                     "ConditionDB_ID", "Synonyms")))

MULTI_VALUE_SEP = ','

def processSubmission(submissionSet, assembly):
    ra = submissionSet.referenceAssertion

    if ra.variant is None:
        logging.warn("No variant information could be extracted for ReferenceClinVarAssertion ID %s %s",
                     submissionSet.referenceAssertion.id, [c.accession for c in submissionSet.otherAssertions.itervalues()])
        return None

    for oa in submissionSet.otherAssertions.values():
        submitter = oa.submitter
        variant = ra.variant
        if oa.origin == "germline":
            hgvs = re.sub("\(" + "(BRCA[1|2])" + "\)",
                          "", variant.name.split()[0])
            proteinChange = None
            if variant.attribute.has_key("HGVS, protein, RefSeq"):
                proteinChange = variant.attribute["HGVS, protein, RefSeq"]
            chrom = None
            start = None
            referenceAllele = None
            alternateAllele = None
            if assembly in variant.coordinates:
                genomicData = variant.coordinates[assembly]
                chrom = genomicData.chrom
                start = genomicData.start
                referenceAllele = genomicData.referenceAllele
                alternateAllele = genomicData.alternateAllele
                genomicCoordinate = "chr%s:%s:%s>%s" % (chrom, start, referenceAllele,
                                                        alternateAllele)

                synonyms = MULTI_VALUE_SEP.join(ra.synonyms + oa.synonyms)

                # Omit the variants that don't have any genomic start coordinate indicated.
                if start != None and start != "None" and start != "NA":
                    print("\t".join((str(hgvs),
                                     oa.submitter.encode('utf-8'),
                                     str(oa.clinicalSignificance),
                                     str(oa.dateLastUpdated),
                                     str(oa.dateSignificanceLastEvaluated),
                                     str(oa.accession),
                                     str(oa.accession_version),
                                     str(oa.id),
                                     str(oa.origin),
                                     str(oa.method),
                                     genomicCoordinate,
                                     str(variant.geneSymbol),
                                     str(proteinChange),
                                     str(oa.description),
                                     str(oa.summaryEvidence),
                                     str(oa.reviewStatus),
                                     str(ra.condition_type),
                                     str(ra.condition_value),
                                     ",".join(ra.condition_db_id) if isinstance(ra.condition_db_id, list) else str(ra.condition_db_id),
                                     str(synonyms))))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("clinVarXmlFilename")
    parser.add_argument('-a', "--assembly", default="GRCh38")
    args = parser.parse_args()

    printHeader()

    inputBuffer = ""
    with open(args.clinVarXmlFilename) as inputFile:
        inClinVarSet = False
        for line in inputFile:
            if "<ClinVarSet" in line:
                inHeader = False
                inputBuffer = line
                inClinVarSet = True
            elif "</ClinVarSet>" in line:
                inputBuffer += line
                inClinVarSet = False

                cvs = ET.fromstring(inputBuffer)
                if clinvar.isCurrent(cvs):
                    submissionSet = clinvar.clinVarSet(cvs)
                    processSubmission(submissionSet, args.assembly)
                inputBuffer = None
            elif inClinVarSet:
                inputBuffer += line

if __name__ == "__main__":
    # execute only if run as a script
    main()
