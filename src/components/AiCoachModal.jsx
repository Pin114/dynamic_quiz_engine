
export default function AiCoachModal({ text, onClose }) {
  return (
    <div className="modal fade show d-block" tabIndex="-1" style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}>
      <div className="modal-dialog modal-dialog-centered">
        <div className="modal-content">
          <div className="modal-header bg-info text-white">
            <h5 className="modal-title">AI 教練</h5>
            <button type="button" className="btn-close btn-close-white" onClick={onClose}></button>
          </div>
          <div className="modal-body">
            <p className="mb-0">{text}</p>
          </div>
          <div className="modal-footer">
            <button type="button" className="btn btn-primary" onClick={onClose}>
              我懂了
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
