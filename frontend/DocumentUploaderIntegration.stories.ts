// DocumentUploader.stories.js
export default {
  title: 'DocumentUploaderIntegration'
};

export const Default = () => ({
  template: `
    <div 
      class="osis-document-uploader" 
      data-name="signature" 
      id="id_signature" 
      data-limit="0" 
      data-base-url="https://test.documents.osis.uclouvain.be/" 
      data-mimetypes="image/jpeg,image/png" 
      data-max-size="524288000" 
      data-max-files="1" 
      data-min-files="0" 
      post_processing="[]"
    ></div>
  `
});