"""
ClinVarUtils: basic
"""


def isCurrent(element):
    """Determine if the indicated clinvar set is current"""
    rr = element.find("RecordStatus")
    if rr == None:
        return False
    else:
        return(rr.text == "current")

def textIfPresent(element, field):
    """Return the text associated with a field under the element, or
    None if the field is not present"""
    ff = element.find(field)
    if ff == None or ff.text == None:
        return None
    else:
        return(ff.text.encode('utf-8'))


def processClinicalSignificanceElement(el, obj):
    if el != None:
        obj.reviewStatus = textIfPresent(el, "ReviewStatus")
        obj.clinicalSignificance = textIfPresent(el, "Description")
        obj.summaryEvidence = textIfPresent(el, "Comment")
        obj.dateSignificanceLastEvaluated = el.get('DateLastEvaluated', None)
    else:
        obj.reviewStatus = None
        obj.clinicalSignificance = None
        obj.summaryEvidence = None
        obj.dateSignificanceLastEvaluated = None


def extractSynonyms(el):
    include_types = {'ProteinChange3LetterCode', 'ProteinChange1LetterCode',
                     'nucleotide change', 'protein change, historical'}
    include_types_norm = {s.lower() for s in include_types}

    exclude_hgvs = {'HGVS, protein, RefSeq', 'HGVS, coding, RefSeq'}
    exclude_hgvs_norm = {s.lower() for s in exclude_hgvs}

    sy_alt = [a.text for a in el.findall(
        'MeasureSet/Measure/Name/ElementValue') if a.get('Type').lower() ==
              'alternate']

    sy = []
    for a in el.findall('MeasureSet/Measure/AttributeSet/Attribute'):
        type = a.get('Type').lower()
        if type in include_types_norm or ('hgvs' in type and type
                                               not in exclude_hgvs_norm):
            sy.append(a.text)

    return sy + sy_alt

class genomicCoordinates:
    """Contains the genomic information on the variant"""

    def __init__(self, element, useNone=False, debug=False):
        if debug:
            print("Parsing genomic coordinates")
        if useNone:
            self.element = None
            self.chrom = None
            self.start = None
            self.stop = None
            self.length = None
            self.referenceAllele = None
            self.alternateAllele = None
        else:
            self.element = element
            self.chrom = element.get("Chr")
            self.stop = element.get("stop")
            self.length = element.get("variantLength")
            self.start = element.get("positionVCF")
            self.referenceAllele = element.get("referenceAlleleVCF")
            self.alternateAllele = element.get("alternateAlleleVCF")


class variant:
    """The Measure set.  We are interested in the variants specifically,
    but measure sets can be other things as well, such as haplotypes"""

    def __init__(self, element, name, id, debug=False):
        self.element = element
        self.id = id
        if debug:
            print("Parsing variant", self.id)
        self.name = name

        self.attribute = dict()
        for attrs in element.findall("AttributeSet"):
            for attrib in attrs.findall("Attribute"):
                self.attribute[attrib.get("Type")] = attrib.text

        self.coordinates = dict()
        for item in element.findall("SequenceLocation"):
            assembly = item.get("Assembly")
            genomic = genomicCoordinates(item, debug=debug)
            self.coordinates[assembly] = genomic
        self.geneSymbol = None
        symbols = element.findall("MeasureRelationship/Symbol")
        for symbol in symbols:
            symbol_val = textIfPresent(symbol, "ElementValue")
            if symbol_val.startswith('BRCA'):
                self.geneSymbol = symbol_val


class referenceAssertion:
    """For gathering the reference assertion"""

    def __init__(self, element, debug=False):
        self.element = element
        self.id = element.get("ID")
        if debug:
            print("Parsing ReferenceClinVarAssertion", self.id)

        processClinicalSignificanceElement(element.find(
            "ClinicalSignificance"), self)


        obs = element.find("ObservedIn")
        if obs == None:
            self.origin = None
            self.ethnicity = None
            self.geographicOrigin = None
            self.age = None
            self.gender = None
            self.familyData = None
            self.method = None
        else:
            sample = obs.find("Sample")
            if sample != None:
                self.origin = textIfPresent(sample, "Origin")
                self.ethnicity = textIfPresent(sample, "Ethnicity")
                self.geographicOrigin = textIfPresent(sample, "GeographicOrigin")
                self.age = textIfPresent(sample, "Age")
                self.gender = textIfPresent(sample, "Gender")
                self.familyData = textIfPresent(sample, "FamilyData")
            method = obs.find("Method")
            if method != None:
                self.method = textIfPresent(method, "MethodType")
        self.variant = None
        self.synonyms = []

        measureSet = element.find("MeasureSet")
        #if measureSet.get("Type") == "Variant":
        if debug:
            if len(measureSet.findall("Measure")) > 1:
                print(self.id, "has multiple measures")
        if len(measureSet.findall("Measure")) == 1:
            name = measureSet.find("Name")
            if name == None:
                variantName = none
            else:
                variantName = name.find("ElementValue").text
            self.variant = variant(measureSet.find("Measure"), variantName,
                                   measureSet.get("ID"),
                                   debug=debug)

        self.synonyms = extractSynonyms(element)

        # extract condition
        self.condition_type = None
        self.condition_value = None
        self.condition_db_id = None
        traitSet = element.find("TraitSet")
        if traitSet != None:
            self.condition_type = traitSet.attrib["Type"]
            trait = traitSet.find("Trait")
            if trait != None:
                names = trait.findall("Name")
                if names != None and len(names) > 0:
                    for name in names:
                        ev = name.find("ElementValue")
                        if ev != None and ev.attrib["Type"] == "Preferred":
                            self.condition_value = textIfPresent(name, "ElementValue")
                        break
                xrefs = trait.findall("XRef")
                if xrefs != None and len(xrefs) > 0:
                    self.condition_db_id = []
                    for xref in xrefs:
                        self.condition_db_id.append(xref.attrib["DB"] + "_" + xref.attrib["ID"])


class clinVarAssertion:
    """Class for representing one submission (i.e. one annotation of a
    submitted variant"""

    def __init__(self, element, debug=False):
        self.element = element
        self.id = element.get("ID")
        if debug:
            print("Parsing ClinVarAssertion", self.id)
        cvsd = element.find("ClinVarSubmissionID")
        if cvsd == None:
            self.submitter = None
            self.dateSubmitted = None
        else:
            self.submitter = cvsd.get("submitter", default=None)
            self.dateSubmitted = cvsd.get("submitterDate")
        cva = element.find("ClinVarAccession")
        if cva == None:
            self.accession = None
        else:
            self.accession = cva.get("Acc", default=None)
            self.accession_version = cva.get("Version", default=None)

        self.origin = None
        self.method = None
        self.description = None
        oi = element.find("ObservedIn")
        if oi != None:
            sample = oi.find("Sample")
            if sample != None:
                self.origin = textIfPresent(sample, "Origin")
            method = oi.find("Method")
            if method != None:
                self.method = textIfPresent(method, "MethodType")
            description = oi.find("ObservedData")
            if description != None:
                for attr in description.findall("Attribute"):
                    if attr.attrib["Type"] == 'Description':
                        self.description = textIfPresent(description, "Attribute")

        processClinicalSignificanceElement(element.find(
            "ClinicalSignificance"), self)

        self.dateLastUpdated = cva.get("DateUpdated")

        self.synonyms = extractSynonyms(element)


class clinVarSet:
    """Container class for a ClinVarSet record, which is a set of submissions
    that were submitted to ClinVar together.  In the ClinVar terminology,
    each ClinVarSet is one aggregate record ("RCV Accession"), which contains
    one or more submissions ("SCV Accessions").
    """

    def __init__(self, element, debug=False):
        self.element = element
        self.id = element.get("ID")
        if debug:
            print("Parsing ClinVarSet ID", self.id)
        rcva = element.find("ReferenceClinVarAssertion")
        if isCurrent(rcva):
            self.referenceAssertion = referenceAssertion(rcva, debug=debug)
        self.otherAssertions = dict()
        for item in element.findall("ClinVarAssertion"):
            if isCurrent(item):
                cva = clinVarAssertion(item)
                accession = cva.accession
                self.otherAssertions[accession] = cva
