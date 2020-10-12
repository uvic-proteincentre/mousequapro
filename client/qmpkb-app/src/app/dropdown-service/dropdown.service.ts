import { Injectable } from '@angular/core';
import {Select} from '../dropdown-service/select';
import {Where} from '../dropdown-service/where';
import {QmpkbService} from '../qmpkb-service/qmpkb.service';



@Injectable({
  providedIn: 'root'
})
export class DropdownService {

  constructor(private _qmpkb:QmpkbService) {
  }

  getSelect(){
    return [
     new Select('Protein', 'protein' ),
     new Select('Gene', 'gene' ),
     new Select('UniProtKB accession', 'uniProtKBAccession'),
     new Select('Peptide sequence', 'pepSeq' ),
     new Select('Panel', 'panel' ),
     new Select('Strain', 'strain' ),
     new Select('Mutant', 'mutant'  ),
     new Select('Sex', 'sex'  ),
     new Select('Biological matrix', 'biologicalMatrix'  ),
     new Select('Subcellular localization', 'subCellLoc' ),
     new Select('Molecular pathway(s)', 'keggPathway' ),
     new Select('Involvement in disease', 'disCausMut' ),
     new Select('GO ID', 'goId' ),
     new Select('GO term', 'goTerm' ),
     new Select('GO aspects', 'goAspects' ),
     new Select('Drug associations ID', 'drugId' ),
     new Select('Own protein sequences in FASTA format', 'fastaFile'  )
    
    ];
  }
  getWhere(){
    return this._qmpkb.dropDownStorage;
  }
}