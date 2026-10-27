// Local OCR aid for font-encoded primary PDFs. OCR is a navigation aid;
// mathematical formulas and source dates require visual page inspection.
import Foundation
import PDFKit
import Vision
import AppKit
let args = CommandLine.arguments
guard args.count >= 3, let pdf = PDFDocument(url: URL(fileURLWithPath: args[1])) else {
    fatalError("usage: read_pdf PDF one_based_page...")
}
for text in args.dropFirst(2) {
    guard let pageNumber = Int(text), let page = pdf.page(at: pageNumber-1) else { fatalError("page") }
    let rect = page.bounds(for: .mediaBox)
    let image = page.thumbnail(of: NSSize(width: 1800, height: 1800*rect.height/rect.width), for: .mediaBox)
    var imageRect = CGRect(origin: .zero, size: image.size)
    guard let cg = image.cgImage(forProposedRect: &imageRect, context: nil, hints: nil) else { fatalError("image") }
    let request = VNRecognizeTextRequest()
    request.recognitionLevel = .accurate
    request.recognitionLanguages = ["de-DE", "en-US", "fr-FR"]
    request.usesLanguageCorrection = true
    try VNImageRequestHandler(cgImage: cg).perform([request])
    print("\n=== PDF PAGE \(pageNumber) ===")
    for observation in request.results ?? [] { if let result = observation.topCandidates(1).first { print(result.string) } }
}
